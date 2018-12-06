<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ajout Annonce </title>
<meta property="og:url" content="http://www.valeron.net/index.html" />
<meta property="og:type" content="website" />
<meta property="og:title" content="Free responsive web template Istria - Contact" />
<meta property="og:description" content="Free responsive web template Istria by Valeron design studio - Contact" />
<meta property="og:image" content="http://www.valeron.net/img/valeron-artist.jpg" />
<meta name="description" content="Free responsive web template Istria by Valeron design studio - Contact" />
<meta name="msapplication-tap-highlight" content="no" />
<meta name="robots" content="index,follow,all" />
<meta name="keywords" content="Izrada web stranica, web studio Istra" />
<meta name="author" content="Valeron design studio" />
<link rel="apple-touch-icon" sizes="57x57" href="img/apple-touch-icon-57x57.png">
<link rel="apple-touch-icon" sizes="60x60" href="img/apple-touch-icon-60x60.png">
<link rel="apple-touch-icon" sizes="72x72" href="img/apple-touch-icon-72x72.png">
<link rel="apple-touch-icon" sizes="76x76" href="img/apple-touch-icon-76x76.png">
<link rel="apple-touch-icon" sizes="114x114" href="img/apple-touch-icon-114x114.png">
<link rel="apple-touch-icon" sizes="120x120" href="img/apple-touch-icon-120x120.png">
<link rel="apple-touch-icon" sizes="144x144" href="img/apple-touch-icon-144x144.png">
<link rel="apple-touch-icon" sizes="152x152" href="img/apple-touch-icon-152x152.png">
<link rel="apple-touch-icon" sizes="180x180" href="img/apple-touch-icon-180x180.png">
<link rel="icon" type="image/png" href="img/favicon-32x32.png" sizes="32x32">
<link rel="icon" type="image/png" href="img/android-chrome-192x192.png" sizes="192x192">
<link rel="icon" type="image/png" href="img/favicon-96x96.png" sizes="96x96">
<link rel="icon" type="image/png" href="img/favicon-16x16.png" sizes="16x16">
<link rel="manifest" href="img/manifest.json">
<meta name="msapplication-TileColor" content="#da532c">
<meta name="msapplication-TileImage" content="img/mstile-144x144.png">
<meta name="theme-color" content="#ffffff">
<link rel="stylesheet" href="css/animsition.min.css">
<link rel="stylesheet" type="text/css" href="css/grid.min.css" />
<link rel="stylesheet" type="text/css" href="css/style.css" />
<link rel="stylesheet" type="text/css" href="css/menu.css" />
<link rel="stylesheet" href="css/banner.css">
<link rel="stylesheet" type="text/css" href="css/social.css" />
<link rel="stylesheet" type="text/css" href="css/slickform.css" />
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/3.5.1/animate.min.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.5.0/css/font-awesome.min.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome-animation/0.0.8/font-awesome-animation.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/modernizr/2.8.3/modernizr.min.js"></script>
</head>
<body>
<div class="animsition-overlay">
  <div class="horBar2Bxx wow fadeInLeftBig" data-wow-duration="3s"></div>
  <header class="main_h">
    <div class="menufix"> <a class="logo" href="index.html"><img src="images/iway.png" alt="Hello"></a>
      <div class="mobile-toggle"> <span></span> <span></span> <span></span> </div>
      <nav>
        <ul>
          <li class="line"><a class="out animsition-link" href="indexadmin.html">ACCUEIL</a></li>
             <li class="line"><a class="out animsition-link" href="blogAdmin.php">EQUIPE</a></li>
            <li class="line"><a class="out animsition-link" href="company.php">ANNONCES</a></li>

          <li class="line"><a class="out animsition-link" href="../../inscription.html">DECONNEXION</a></li>
        </ul>
      </nav>
    </div>
    <!-- / row --> 
    
  </header>
  <div class="grid flex16">
    <div class="row">
      <div class="colw_6">
        <h1 id="title-sub1">I - Way</h1>
        <h2 id="title-sub2">Ajouter annonce</h2>
      </div>
      <!-- END colw_6 -->
      
              <div class="col_6">
        <div class="bannerbox">
          <div class="banner">
            <div class="phrase-1">Ajouter des Annonces</div>
            <div class="phrase-2"><a href="formannonce.html"  > Ajouter </a></div>
            <div class="blob-1"></div>
            <div class="blob-2"></div>
            <div class="blob-3"></div>
          </div>
        </div>
      </div>
      <!-- END col_6 --> 
      
    </div>
    <!-- END row --> 
    
  </div>
  <!-- End GRID FLEX16 -->
  
      <div class="colw_6 spec-r-cont border-right ">

        <div class="slickwrap">
          <div class="slickreporting">
            <div class="successcontainer"></div>
            <div class="errorcontainer">
              <div class="errorshutter"></div>
              <div class="slickerror"></div>
            </div>
          </div>
             <center>
           <img src="../../images/annonce.jpg" alt="annonce" ></center>
              <hr />
        </div>
        </div>
      <!-- END col_12 --><!-- END col_6 -->
      
      <div class="colw_6 paddbott100 spec-r-cont" >
        <h3>Ajout Annonce</h3>
        <div class="slickwrap">
          <div class="slickreporting">
            <div class="successcontainer"></div>
            <div class="errorcontainer">
            
              <div class="errorshutter"></div>
              <div class="slickerror"></div>
            </div>
          </div>
  <?php
include"../Classes/annonce.class.php";
$p=new annonce();
$row=$p->selection_id($_GET['numAnnonce']);
?>
          <form method="post" action="../Controlleurs/traitModifAnn.php">
            <fieldset>
              
              <input name="numAnnonce" type="hidden" value="<?php echo $row[0]?>">
              <br />
              <label><span></span>Profil</label>
              <input id="poste" name="poste" type="text" value="<?php echo $row[1]?>">
              <br /><br /> 
              <label><span></span>Expérience</label>
              <input  name="experience" type="text" value="<?php echo $row[2]?>">
              <br /><br />
              <label><span></span>Compétence </label>
              <textarea name="competence"  cols="5" rows="5" class="largertextarea" ><?php echo $row[3]?></textarea>
              <br />
 
               <label><span></span>Salaire</label>
              <input  name="salaire" type="text" value="<?php echo $row[4]?>">
               
              <br /><br /> 
               <label><span></span>Date d'annonce</label>
              <input  name="dateAnnonce" type="date" value="<?php echo $row[5]?>">
              
             
              <hr />
              <input name="submit" type="submit" value="Modifier" class="slickbutton">
            </fieldset>
          </form>
        </div>
      </div>
      <!-- END col_6 --> 
      

<!-- END .animsition-overlaj --> 

<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js"></script> 
<script type="text/javascript" src="js/jquery.matchHeight-min.js"></script> 
<script src="js/wow.min.js"></script> 
<script src="js/animsition.min.js"></script> 
<script src="js/Slickform.js"></script> 
<script src="js/functions.js"></script> 
<script type="text/javascript">
  var _gaq = _gaq || [];
  _gaq.push(['_setAccount', 'UA-15815880-3']);
  _gaq.push(['_trackPageview']);
  (function() {
    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
  })();
</script>
</body>
</html>