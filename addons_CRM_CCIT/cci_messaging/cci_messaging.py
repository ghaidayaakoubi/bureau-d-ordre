# -*- coding: utf-8 -*-
import base64
import tempfile
import logging
from email.utils import formataddr
from urlparse import urljoin

import psycopg2

from openerp import api, tools
from openerp import SUPERUSER_ID
from openerp.addons.base.ir.ir_mail_server import MailDeliveryException
from openerp.osv import fields, osv
from openerp.tools.safe_eval import safe_eval as eval
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)


class cci_messaging(osv.Model):
	""" Model holding RFC2822 email messages to send. This model also provides
		facilities to queue and send new email messages.  """
	_name = 'cci.messaging'
	_description = 'Messagerie personelle'
	_inherit = "mail.mail"

	_columns = {
		#add control readonly with state by marwa 10-10-2017

		'email_bcc': fields.char('Cci',readonly=True, states={'outgoing':[('readonly', False)]}),
		'state': fields.selection([
			('outgoing', 'Sortant'),
			('sent', 'Envoyé'),
			('received', 'Reçu'),
			('exception', "Échec de l'envoi"),
			('cancel', 'Annulé'),
		], 'Status', readonly=True, copy=False),

		'recipient_ids': fields.many2many('res.partner',readonly=True, states={'outgoing':[('readonly', False)]}),

	}
	#add by marwa BM 10-10-2017
	def message_redirect_action(self, cr, uid, context=None):
		""" For a given message, return an action that either
		    - opens the form view of the related document if model, res_id, and
		      read access to the document
		    - opens the Inbox with a default search on the conversation if model,
		      res_id
		    - opens the Inbox with context propagated

		"""
		if context is None:
		    context = {}
		#super(subClass, instance).method(args)
		action=self.pool.get('mail.thread').message_redirect_action(cr, uid, context=context)
		return action

	def get_attachments(self,cr,uid,ids,context=None):
		active_record = self.browse(cr, uid, ids[0], context=context)
		mail_attachments_ids = self.pool.get('cci.document.alfresco.message').search(cr, uid, [
			('message_id', "=", active_record.id)], context=context)

		active_record_attachments = self.pool.get('cci.document.alfresco.message').browse(cr, uid,
																						  mail_attachments_ids,
																						  context=context)
		if active_record_attachments:
			self.create_attachments(cr,uid,ids,active_record_attachments,context=None)
			return True


	def create_attachments(self, cr, uid, ids,attach_objs, context=None):
		active_record = self.browse(cr, uid, ids[0], context=context)
		for attach in attach_objs:
			repo = self.pool.get('cci.alfresco.configuration').connection_alfresco_old_api(cr, uid, context=context)

			doc = repo.getObject(attach.node)
			result = doc.getContentStream()
			fobj = tempfile.NamedTemporaryFile(delete=False)
			fname = fobj.name
			fobj.write(result.read())
			fobj.close()

			with open(fname, "rb") as file:
				file_base64 = base64.encodestring(file.read())
				self.pool.get('ir.attachment').create(cr, uid, {'datas': file_base64, 'datas_fname': attach.nom_fichier,
																'name': attach.nom_fichier, 'res_id': active_record.id,
																'res_model':active_record._name}, context=context)


	def send(self, cr, uid, ids, auto_commit=False, raise_exception=False, context=None):
		recipient_ids = []
		attachment_ids =[]
		attachments =[]

		context = dict(context or {})
		list_recipient_ids = []
		ir_mail_server = self.pool.get('ir.mail_server')
		ir_attachment = self.pool['ir.attachment']
		thread_pool = self.pool.get('mail.thread')

		for mail in self.browse(cr, SUPERUSER_ID, ids, context=context):
			try:
				# TDE note: remove me when model_id field is present on mail.message - done here to avoid doing it multiple times in the sub method
				if mail.model:
					model_id = \
					self.pool['ir.model'].search(cr, SUPERUSER_ID, [('model', '=', mail._name)], context=context)[0]
					model = self.pool['ir.model'].browse(cr, SUPERUSER_ID, model_id, context=context)
				else:
					model = None
				if model:
					context['model_name'] = model.name

				# -------------------------Choix du serveur SMTP----------------------
				try:
					mail_server_id = self.pool.get('ir.mail_server').search(cr,uid,[('user_id','=',uid)])[0]

				except:
					mail_server_id = self.pool.get('ir.mail_server').search(cr, uid, [])[0]

				# -------------------------récupération des pièces jointes----------------------------------------------
				res = self.get_attachments(cr, uid, ids, context=None)

				if res :

					attachment_ids = self.pool.get('ir.attachment').search(cr, uid, [('res_id', "=", mail.id), (
						'res_model', "like", mail._name)], context=context)

					attachments = [(a['datas_fname'], base64.b64decode(a['datas']))
								   for a in ir_attachment.read(cr, SUPERUSER_ID, attachment_ids,
															   ['datas_fname', 'datas'])]
				else:
					pass
				#-------------------------------------------------------------------------------------------------------
				# specific behavior to customize the send email for notified partners
				email_list = []
				if mail.email_to:
					email_list.append(self.send_get_email_dict(cr, uid, mail, context=context))
				for partner in mail.recipient_ids:
					email_list.append(self.send_get_email_dict(cr, uid, mail, partner=partner, context=context))

				# headers
				headers = {}
				bounce_alias = self.pool['ir.config_parameter'].get_param(cr, uid, "mail.bounce.alias", context=context)
				catchall_domain = self.pool['ir.config_parameter'].get_param(cr, uid, "mail.catchall.domain",
																			 context=context)
				if bounce_alias and catchall_domain:
					if mail.model and mail.res_id:
						headers['Return-Path'] = '%s-%d-%s-%d@%s' % (
						bounce_alias, mail.id, mail.model, mail.res_id, catchall_domain)
					else:
						headers['Return-Path'] = '%s-%d@%s' % (bounce_alias, mail.id, catchall_domain)
				if mail.headers:
					try:
						headers.update(eval(mail.headers))
					except Exception:
						pass

				# Writing on the mail object may fail (e.g. lock on user) which
				# would trigger a rollback *after* actually sending the email.
				# To avoid sending twice the same email, provoke the failure earlier
				mail.write({'state': 'exception'})
				mail_sent = False

				# build an RFC2822 email.message.Message object and send it without queuing
				res = None
				for email in email_list:
					msg = ir_mail_server.build_email(
						email_from=mail.email_from,
						email_to=email.get('email_to'),
						subject=email.get('subject'),
						body=email.get('body'),
						body_alternative=email.get('body_alternative'),
						email_cc=tools.email_split(mail.email_cc),
						email_bcc=tools.email_split(mail.email_bcc),
						reply_to=mail.reply_to,
						attachments=attachments,
						message_id=mail.message_id,
						references=mail.references,
						object_id=mail.res_id and ('%s-%s' % (mail.res_id, mail.model)),
						subtype='html',
						subtype_alternative='plain',
						headers=headers)
					try:
						res = ir_mail_server.send_email(cr, uid, msg,
														mail_server_id=mail_server_id,
														context=context)
					except AssertionError as error:
				# ------------suppresion des pieces jointes de ir attachments en cas d'echec d'envoi
				# pour ne pas les renvoyer dans la prochaine tentative------------------------------

						self.pool.get('ir.attachment').unlink(cr, uid, attachment_ids, context=None)
				# --------------------------------------------------------------------------------
						if error.message == ir_mail_server.NO_VALID_RECIPIENT:
							# No valid recipient found for this particular
							# mail item -> ignore error to avoid blocking
							# delivery to next recipients, if any. If this is
							# the only recipient, the mail will show as failed.
							_logger.warning("Ignoring invalid recipients for cci.messaging %s: %s",
											mail.message_id, email.get('email_to'))

						else:
							raise
				if res:
					mail.write({'state': 'sent', 'message_id': res})
					mail_sent = True


					# -------------------------récupération des partenaires-----------------------------
					for rec in mail.recipient_ids:
						list_recipient_ids.append(rec.id)
					partner_ids = [(4, partner_id) for partner_id in list_recipient_ids]

					post_vars = {
						'record_name': mail.subject,
						'model': mail._name,
						'res_id': mail._name and mail.id or False,
						'body': mail.body,
						'subject': mail.subject or False,
						'partner_ids': partner_ids,
						'attachment_ids': attachment_ids,
					}
					# notif_type permet de envoyer seulement une notification à l'utilisateur dans son messagerie sans lui envoyer un mail
					notif_type = {'mail_notify_noemail': True}

					# """:param int thread_id: thread ID to post into, or list with one ID;"
					# if False/0, mail.message model will also be set as False"""

					thread_pool.message_post(cr, uid, False, type="notification", subtype="mt_comment",
											 context=notif_type, **post_vars)
					thread_id = thread_pool.browse(cr, uid, ids, context=context).id

					# def write(self, cr, uid, ids, values, context=None):
					thread_update = self.write(cr, uid, thread_id,
											   {'res_id': mail._name and mail.id, 'model': mail._name}, context=context)

					message = self.pool.get('mail.message').search(cr, uid, [('subject', '=', mail.subject)],
																   context=context)

					mail_model = self.pool.get('cci.messaging')
					self.pool.get('mail.message').write(cr, uid, message,
														{'res_id': mail._name and mail.id, 'model': mail_model},
														context=context)

				# /!\ can't use mail.state here, as mail.refresh() will cause an error
				# see revid:odo@openerp.com-20120622152536-42b2s28lvdv3odyr in 6.1
				if mail_sent:
					_logger.info('Mail with ID %r and Message-Id %r successfully sent', mail.id, mail.message_id)
				self._postprocess_sent_message(cr, uid, mail, context=context, mail_sent=mail_sent)
			except MemoryError:
				# prevent catching transient MemoryErrors, bubble up to notify user or abort cron job
				# instead of marking the mail as failed
				_logger.exception('MemoryError while processing mail with ID %r and Msg-Id %r. ' \
								  'Consider raising the --limit-memory-hard startup option',
								  mail.id, mail.message_id)
				raise
			except psycopg2.Error:
				# If an error with the database occurs, chances are that the cursor is unusable.
				# This will lead to an `psycopg2.InternalError` being raised when trying to write
				# `state`, shadowing the original exception and forbid a retry on concurrent
				# update. Let's bubble it.
				raise
			except Exception as e:
				_logger.exception('failed sending cci.messaging %s', mail.id)
				mail.write({'state': 'exception'})
				self._postprocess_sent_message(cr, uid, mail, context=context, mail_sent=False)
				if raise_exception:
					if isinstance(e, AssertionError):
						# get the args of the original error, wrap into a value and throw a MailDeliveryException
						# that is an except_orm, with name and value as arguments
						value = '. '.join(e.args)
						raise MailDeliveryException(_("Mail Delivery Failed"), value)
					raise

			if auto_commit is True:
				cr.commit()
		return True



