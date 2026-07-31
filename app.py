<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Cortex — Des mots à l'image</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Unbounded:wght@400;600;800;900&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
  :root{
    --bg-base:#180f2c;
    --bg-alt:#120a22;
    --bg-card:#231640;
    --ink:#f7f1fb;
    --ink-dim:#c2b3de;
    --coral:#ff5c86;
    --lime:#e6ff6b;
    --violet:#b694ff;
    --line:rgba(247,241,251,0.12);
    --maxw:1180px;
  }

  *{box-sizing:border-box;}
  html{scroll-behavior:smooth;}
  body{
    margin:0;
    background:var(--bg-base);
    color:var(--ink);
    font-family:'Plus Jakarta Sans', sans-serif;
    -webkit-font-smoothing:antialiased;
    overflow-x:hidden;
  }
  h1,h2,h3{
    font-family:'Unbounded', sans-serif;
    margin:0;
    line-height:1.05;
    letter-spacing:-0.01em;
  }
  .mono{ font-family:'Space Mono', monospace; }
  p{color:var(--ink-dim); line-height:1.65; margin:0;}
  a{color:inherit;}
  section{position:relative; padding:120px 24px;}
  .wrap{max-width:var(--maxw); margin:0 auto; position:relative;}
  .eyebrow{
    display:inline-flex; align-items:center; gap:10px;
    font-family:'Space Mono', monospace;
    font-size:13px; letter-spacing:0.14em; text-transform:uppercase;
    color:var(--lime); margin-bottom:22px;
  }
  .eyebrow::before{
    content:''; width:8px; height:8px; border-radius:50%;
    background:var(--coral); box-shadow:0 0 0 4px rgba(255,92,134,0.2);
  }
  .btn{
    display:inline-flex; align-items:center; gap:8px;
    padding:14px 26px; border-radius:100px;
    font-family:'Plus Jakarta Sans', sans-serif; font-weight:700; font-size:15px;
    text-decoration:none; border:1px solid transparent; cursor:pointer;
    transition:transform .25s ease, box-shadow .25s ease;
  }
  .btn:hover{transform:translateY(-2px);}
  .btn-primary{background:linear-gradient(120deg, var(--coral), var(--violet)); color:#160a26; box-shadow:0 10px 30px -10px rgba(255,92,134,0.6);}
  .btn-ghost{border-color:var(--line); color:var(--ink);}
  .btn-ghost:hover{border-color:var(--lime);}

  #scrub{
    position:fixed; top:0; left:0; right:0; height:64px; z-index:100;
    display:flex; align-items:center; padding:0 24px;
    background:linear-gradient(180deg, rgba(18,10,34,0.92), rgba(18,10,34,0));
    backdrop-filter:blur(6px);
  }
  .scrub-inner{max-width:var(--maxw); width:100%; margin:0 auto; display:flex; align-items:center; gap:22px;}
  .wordmark{font-family:'Unbounded', sans-serif; font-weight:800; font-size:19px; letter-spacing:-0.02em; white-space:nowrap;}
  .wordmark span{color:var(--coral);}
  .track{ position:relative; flex:1; height:3px; background:var(--line); border-radius:3px; display:flex; align-items:center; }
  .track-fill{ position:absolute; left:0; top:0; height:100%; width:0%; background:linear-gradient(90deg, var(--coral), var(--violet)); border-radius:3px; }
  .marker{ position:absolute; top:50%; transform:translate(-50%,-50%); width:9px; height:9px; border-radius:50%; background:var(--bg-base); border:2px solid var(--ink-dim); cursor:pointer; z-index:2; }
  .marker.active{background:var(--lime); border-color:var(--lime);}
  .playhead{ position:absolute; top:50%; transform:translate(-50%,-50%); width:13px; height:13px; border-radius:50%; background:var(--ink); box-shadow:0 0 0 5px rgba(247,241,251,0.15); left:0%; z-index:3; transition:left .08s linear; }
  #timecode{font-family:'Space Mono', monospace; font-size:13px; color:var(--ink-dim); white-space:nowrap; min-width:56px;}
  .nav-links{display:flex; gap:18px; font-size:14px; color:var(--ink-dim);}
  .nav-links a:hover{color:var(--lime);}
  @media (max-width:900px){ .nav-links{display:none;} }

  .hero{padding-top:180px; padding-bottom:100px; overflow:hidden;}
  .hero-grid{display:grid; grid-template-columns:1.1fr 0.9fr; gap:60px; align-items:center;}
  @media (max-width:940px){ .hero-grid{grid-template-columns:1fr;} }
  .hero h1{font-size:clamp(38px, 5.6vw, 68px); font-weight:900;}
  .hero h1 em{font-style:normal; color:transparent; background:linear-gradient(120deg,var(--coral),var(--lime)); -webkit-background-clip:text; background-clip:text;}
  .hero p.lead{margin-top:24px; font-size:18px; max-width:520px;}
  .hero-ctas{display:flex; gap:14px; margin-top:38px; flex-wrap:wrap;}
  .status-pill{
    display:inline-flex; align-items:center; gap:8px; margin-top:26px;
    padding:8px 16px; border-radius:100px; border:1px solid var(--line);
    font-family:'Space Mono', monospace; font-size:12.5px; color:var(--ink-dim);
  }
  .status-pill i{width:7px; height:7px; border-radius:50%; background:var(--lime); animation:pulse 1.8s ease-in-out infinite;}
  @keyframes pulse{0%,100%{opacity:1;} 50%{opacity:0.3;}}

  .blob{ position:absolute; border-radius:44% 56% 62% 38% / 42% 46% 54% 58%; filter:blur(2px); opacity:0.55; z-index:0; animation:morph 12s ease-in-out infinite alternate; }
  @keyframes morph{ 0%{border-radius:44% 56% 62% 38% / 42% 46% 54% 58%;} 50%{border-radius:58% 42% 40% 60% / 55% 60% 40% 45%;} 100%{border-radius:40% 60% 55% 45% / 60% 40% 60% 40%;} }
  .blob-1{width:420px; height:420px; top:-80px; right:-100px; background:radial-gradient(circle at 30% 30%, var(--coral), transparent 70%);}
  .blob-2{width:280px; height:280px; bottom:-60px; right:180px; background:radial-gradient(circle at 60% 40%, var(--violet), transparent 70%);}

  .sample-card{ position:relative; z-index:1; background:var(--bg-card); border:1px solid var(--line); border-radius:22px; padding:22px; box-shadow:0 30px 60px -30px rgba(0,0,0,0.6); }
  .sample-label{font-family:'Space Mono', monospace; font-size:12px; color:var(--lime); letter-spacing:0.08em; text-transform:uppercase; margin-bottom:14px;}
  .sample-media{ display:grid; grid-template-columns:1fr 1fr; gap:10px; }
  .sample-video{ aspect-ratio:16/10; border-radius:12px; background:linear-gradient(155deg, #ff5c86, #7a4fd6); position:relative; display:flex; align-items:center; justify-content:center; }
  .sample-video::before{ content:'▶'; font-size:18px; color:rgba(255,255,255,0.85); background:rgba(0,0,0,0.25); width:38px; height:38px; border-radius:50%; display:flex; align-items:center; justify-content:center; }
  .sample-audio{ aspect-ratio:16/10; border-radius:12px; background:var(--bg-base); border:1px solid var(--line); display:flex; align-items:center; padding:0 14px; }
  .prompt-row{display:flex; align-items:flex-start; gap:10px; background:var(--bg-base); border:1px solid var(--line); border-radius:14px; padding:12px 14px; margin-top:12px;}
  .prompt-row .dot{width:8px; height:8px; border-radius:50%; background:var(--coral); flex:none; margin-top:5px;}
  .prompt-row span{font-family:'Space Mono', monospace; font-size:12.5px; color:var(--ink-dim); line-height:1.5;}
  .wave{display:flex; align-items:flex-end; gap:2.5px; height:100%; width:100%;}
  .wave i{flex:1; background:var(--ink-dim); opacity:0.5; border-radius:2px; animation:bounce 1.6s ease-in-out infinite;}
  .wave i:nth-child(odd){animation-delay:.15s;}
  .wave i:nth-child(3n){animation-delay:.3s; background:var(--lime); opacity:0.9;}
  @keyframes bounce{0%,100%{height:20%;} 50%{height:90%;}}

  .reveal{opacity:0; transform:translateY(24px); transition:opacity .7s ease, transform .7s ease;}
  .reveal.in{opacity:1; transform:translateY(0);}

  .about-grid{display:grid; grid-template-columns:1fr 1fr; gap:60px; align-items:start;}
  @media (max-width:860px){ .about-grid{grid-template-columns:1fr;} }
  .about-grid h2{font-size:clamp(30px,4vw,44px);}
  .pillars{display:flex; flex-direction:column; gap:22px; margin-top:8px;}
  .pillar{display:flex; gap:16px; align-items:flex-start; border-top:1px solid var(--line); padding-top:18px;}
  .pillar .mono{color:var(--coral); font-size:13px; min-width:34px;}
  .pillar h3{font-size:18px; margin-bottom:6px;}

  section.alt{background:var(--bg-alt);}

  .chain{display:grid; grid-template-columns:repeat(3,1fr); gap:0; margin-top:60px; position:relative;}
  @media (max-width:860px){ .chain{grid-template-columns:1fr; gap:40px;} }
  .chain::before{ content:''; position:absolute; top:26px; left:8%; right:8%; height:2px; background:repeating-linear-gradient(90deg, var(--line) 0 8px, transparent 8px 14px); }
  @media (max-width:860px){ .chain::before{display:none;} }
  .step{position:relative; padding:0 20px;}
  .step-num{ width:52px; height:52px; border-radius:50%; background:var(--bg-card); border:1px solid var(--line); display:flex; align-items:center; justify-content:center; font-family:'Space Mono', monospace; color:var(--lime); font-size:14px; margin-bottom:22px; position:relative; z-index:1; }
  .step h3{font-size:21px; margin-bottom:10px;}

  .tags{display:flex; flex-wrap:wrap; gap:12px; margin-top:34px;}
  .tag{ padding:10px 18px; border-radius:100px; border:1px solid var(--line); font-family:'Space Mono', monospace; font-size:13px; color:var(--ink-dim); background:var(--bg-card); }
  .tag.hi{border-color:var(--lime); color:var(--lime);}

  .trust-grid{display:grid; grid-template-columns:repeat(2,1fr); gap:20px; margin-top:50px;}
  @media (max-width:860px){ .trust-grid{grid-template-columns:1fr;} }
  .trust-card{ background:var(--bg-card); border:1px solid var(--line); border-radius:18px; padding:26px; }
  .trust-card .mono{color:var(--lime); font-size:12px; letter-spacing:0.08em; text-transform:uppercase; display:block; margin-bottom:12px;}
  .trust-card h3{font-size:19px; margin-bottom:10px;}

  .wanted{display:grid; grid-template-columns:repeat(3,1fr); gap:20px; margin-top:50px;}
  @media (max-width:940px){ .wanted{grid-template-columns:repeat(2,1fr);} }
  @media (max-width:640px){ .wanted{grid-template-columns:1fr;} }
  .want-card{border-radius:18px; overflow:hidden; border:1px solid var(--line); background:var(--bg-card); padding:22px;}
  .want-icon{width:40px; height:40px; border-radius:10px; background:linear-gradient(150deg, var(--c1), var(--c2)); margin-bottom:16px;}
  .want-card:nth-child(1) .want-icon{--c1:#ff5c86; --c2:#2b1650;}
  .want-card:nth-child(2) .want-icon{--c1:#b694ff; --c2:#1a1030;}
  .want-card:nth-child(3) .want-icon{--c1:#e6ff6b; --c2:#3a1a3a;}
  .want-card:nth-child(4) .want-icon{--c1:#4fd6c4; --c2:#241246;}
  .want-card:nth-child(5) .want-icon{--c1:#ff9d6b; --c2:#1a1030;}
  .want-card:nth-child(6) .want-icon{--c1:#7a8bff; --c2:#2b1650;}
  .want-card h3{font-size:18px; margin-bottom:8px;}
  .want-card p{font-size:14px;}

  .contact-grid{display:grid; grid-template-columns:1fr 1fr; gap:60px;}
  @media (max-width:860px){ .contact-grid{grid-template-columns:1fr;} }
  form{display:flex; flex-direction:column; gap:14px;}
  input, textarea, select{ background:var(--bg-card); border:1px solid var(--line); border-radius:12px; padding:14px 16px; color:var(--ink); font-family:'Plus Jakarta Sans'; font-size:15px; }
  input:focus, textarea:focus, select:focus{outline:2px solid var(--lime); outline-offset:1px;}
  textarea{resize:vertical; min-height:110px;}
  label{font-size:13px; color:var(--ink-dim); font-family:'Space Mono', monospace;}
  .checkline{display:flex; align-items:flex-start; gap:10px; font-size:13px; color:var(--ink-dim);}
  .checkline input{width:auto; padding:0; margin-top:3px;}

  footer{padding:60px 24px 40px; border-top:1px solid var(--line);}
  .footer-inner{max-width:var(--maxw); margin:0 auto; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px;}
  .footer-inner .mono{font-size:12px; color:var(--ink-dim);}

  @media (prefers-reduced-motion: reduce){
    *{animation:none !important; transition:none !important;}
    html{scroll-behavior:auto;}
  }
</style>
</head>
<body>

<div id="scrub">
  <div class="scrub-inner">
    <div class="wordmark">CORTE<span>X</span></div>
    <div class="track" id="track">
      <div class="track-fill" id="trackFill"></div>
      <div class="playhead" id="playhead"></div>
    </div>
    <div id="timecode" class="mono">00:00</div>
    <div class="nav-links">
      <a href="#about">Manifeste</a>
      <a href="#how">Collecte</a>
      <a href="#trust">Confiance</a>
      <a href="#stack">Stack</a>
      <a href="#wanted">On cherche</a>
      <a href="#contact">Contribuer</a>
    </div>
  </div>
</div>

<section class="hero" id="hero">
  <div class="blob blob-1"></div>
  <div class="blob blob-2"></div>
  <div class="wrap hero-grid">
    <div>
      <div class="eyebrow mono">00:00 — Ouverture</div>
      <h1>On entraîne l'IA<br>qui tournera <em>l'intro.</em></h1>
      <p class="lead">Cortex construit un système qui transforme un simple prompt en clip vidéo d'ouverture pour un morceau, à partir de plusieurs modèles IA open source assemblés. On est en phase de collecte de données : on rassemble des clips vidéo, des morceaux et leurs descriptions pour entraîner le modèle.</p>
      <div class="hero-ctas">
        <a href="#contact" class="btn btn-primary">Contribuer des données</a>
        <a href="#trust" class="btn btn-ghost">Comment on protège vos données</a>
      </div>
      <div class="status-pill"><i></i>Statut actuel : collecte de données — pas encore de modèle entraîné</div>
    </div>
    <div class="sample-card reveal">
      <div class="sample-label">Format d'une contribution</div>
      <div class="sample-media">
        <div class="sample-video"></div>
        <div class="sample-audio"><div class="wave">
          <i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i>
        </div></div>
      </div>
      <div class="prompt-row">
        <div class="dot"></div>
        <span>Prompt associé : « néon rose, ville pluvieuse au ralenti, caméra qui s'élève »</span>
      </div>
    </div>
  </div>
</section>

<section id="about" class="alt">
  <div class="wrap about-grid">
    <div class="reveal">
      <div class="eyebrow mono">00:14 — Qui sommes-nous</div>
      <h2>On code au carrefour<br>de l'image et du son.</h2>
      <p style="margin-top:22px; font-size:16px;">Cortex est un petit collectif qui construit sur la recherche IA open source, pour donner aux musiciens et créateurs un outil qui génère automatiquement l'ouverture visuelle de leurs morceaux à partir d'un prompt. On en est à la première étape, la plus importante : réunir des données de qualité pour entraîner le modèle correctement, plutôt que de brûler les étapes.</p>
    </div>
    <div class="pillars reveal">
      <div class="pillar">
        <span class="mono">01</span>
        <div><h3>Transparence d'abord</h3><p>On dit clairement où on en est : pas de fausse démo, pas de promesse qu'on ne peut pas tenir aujourd'hui.</p></div>
      </div>
      <div class="pillar">
        <span class="mono">02</span>
        <div><h3>Open source</h3><p>La pipeline s'appuiera sur des modèles ouverts, et on republiera nos améliorations à la communauté.</p></div>
      </div>
      <div class="pillar">
        <span class="mono">03</span>
        <div><h3>Respect des contributeurs</h3><p>Chaque personne qui nous donne des données garde ses droits et sait précisément à quoi ça sert.</p></div>
      </div>
    </div>
  </div>
</section>

<section id="how">
  <div class="wrap">
    <div class="reveal">
      <div class="eyebrow mono">00:38 — La collecte</div>
      <h2 style="font-size:clamp(30px,4vw,44px); max-width:640px;">Trois étapes pour transformer votre clip en donnée d'entraînement.</h2>
    </div>
    <div class="chain">
      <div class="step reveal">
        <div class="step-num">01</div>
        <h3>Vous proposez</h3>
        <p>Un clip vidéo, le morceau associé, et une description du style visuel — l'équivalent du prompt qui aurait pu le générer.</p>
      </div>
      <div class="step reveal">
        <div class="step-num">02</div>
        <h3>On vérifie</h3>
        <p>On contrôle les droits, la qualité technique, et on annote la donnée avant qu'elle entre dans le jeu d'entraînement.</p>
      </div>
      <div class="step reveal">
        <div class="step-num">03</div>
        <h3>Ça nourrit le modèle</h3>
        <p>La donnée sert uniquement à entraîner Cortex — jamais revendue, jamais réutilisée pour autre chose sans votre accord.</p>
      </div>
    </div>
  </div>
</section>

<section id="trust" class="alt">
  <div class="wrap">
    <div class="reveal">
      <div class="eyebrow mono">01:00 — Pourquoi nous faire confiance</div>
      <h2 style="font-size:clamp(30px,4vw,44px); max-width:640px;">On sait qu'on vous demande de la confiance avant d'avoir un produit fini.</h2>
    </div>
    <div class="trust-grid">
      <div class="trust-card reveal">
        <span class="mono">Droits</span>
        <h3>Vous restez propriétaire</h3>
        <p>Vous gardez tous les droits sur vos clips et morceaux. On vous demande une licence limitée à l'entraînement, jamais une cession.</p>
      </div>
      <div class="trust-card reveal">
        <span class="mono">Usage</span>
        <h3>Une seule finalité</h3>
        <p>Vos données servent uniquement à entraîner le modèle Cortex. Pas de revente, pas de partage avec des tiers non annoncés.</p>
      </div>
      <div class="trust-card reveal">
        <span class="mono">Sécurité</span>
        <h3>Accès restreint</h3>
        <p>Stockage chiffré, accès limité à l'équipe cœur du projet, suppression possible sur simple demande.</p>
      </div>
      <div class="trust-card reveal">
        <span class="mono">Traçabilité</span>
        <h3>Crédit &amp; suivi</h3>
        <p>Chaque contributeur peut savoir où en est le projet et demander le retrait de ses données à tout moment.</p>
      </div>
    </div>
  </div>
</section>

<section id="stack">
  <div class="wrap reveal">
    <div class="eyebrow mono">01:20 — La stack</div>
    <h2 style="font-size:clamp(30px,4vw,44px); max-width:600px;">Une pipeline pensée, pas encore entraînée.</h2>
    <p style="margin-top:20px; max-width:560px;">Le modèle final combinera plusieurs familles de briques open source, chacune spécialisée sur une étape du clip. Liste à personnaliser avec vos vraies briques :</p>
    <div class="tags">
      <span class="tag hi">Génération vidéo</span>
      <span class="tag">Text-to-image</span>
      <span class="tag">Interpolation de mouvement</span>
      <span class="tag hi">Synthèse & analyse audio</span>
      <span class="tag">Upscaling</span>
      <span class="tag">Colorimétrie automatique</span>
      <span class="tag">Segmentation & rotoscopie</span>
    </div>
  </div>
</section>

<section id="wanted" class="alt">
  <div class="wrap">
    <div class="reveal">
      <div class="eyebrow mono">01:45 — Ce qu'on recherche</div>
      <h2 style="font-size:clamp(30px,4vw,44px); max-width:600px;">Les contributions qui nous aident le plus.</h2>
      <p style="margin-top:16px; max-width:560px;">Pas besoin d'un studio pro. On cherche surtout de la variété et des descriptions précises.</p>
    </div>
    <div class="wanted">
      <div class="want-card reveal"><div class="want-icon"></div><h3>Clips musicaux courts</h3><p>Intros, teasers ou extraits de 5 à 30 secondes, avec le morceau associé.</p></div>
      <div class="want-card reveal"><div class="want-icon"></div><h3>Descriptions précises</h3><p>Le style visuel, la lumière, le mouvement de caméra — le plus détaillé possible.</p></div>
      <div class="want-card reveal"><div class="want-icon"></div><h3>Ambiances variées</h3><p>Néon urbain, nature, studio, animation — la diversité compte plus que le volume.</p></div>
      <div class="want-card reveal"><div class="want-icon"></div><h3>Morceaux avec structure claire</h3><p>Un rythme et une intro identifiables aident le modèle à apprendre le calage.</p></div>
      <div class="want-card reveal"><div class="want-icon"></div><h3>Droits clairs</h3><p>Contenus que vous avez créés ou pour lesquels vous avez l'autorisation de les partager.</p></div>
      <div class="want-card reveal"><div class="want-icon"></div><h3>Retours critiques</h3><p>Même sans clip à donner, vos retours sur le projet et son sérieux nous aident.</p></div>
    </div>
  </div>
</section>

<section id="contact">
  <div class="wrap contact-grid">
    <div class="reveal">
      <div class="eyebrow mono">02:05 — Contribuer</div>
      <h2 style="font-size:clamp(30px,4vw,44px);">Envoyez-nous vos premières données.</h2>
      <p style="margin-top:20px; max-width:460px;">Bêta-testeurs, contributeurs de données, artistes ou curieux de l'open source : dites-nous ce que vous pouvez partager, on revient vers vous rapidement.</p>
    </div>
    <form class="reveal" onsubmit="return false;">
      <input type="text" placeholder="Ton nom" required>
      <input type="email" placeholder="Ton email" required>
      <textarea placeholder="Décris ce que tu peux fournir (clips, morceaux, prompts...) et un lien si tu en as"></textarea>
      <label class="checkline"><input type="checkbox" required> Je confirme être l'auteur ou avoir l'autorisation de partager ce contenu à des fins d'entraînement.</label>
      <button type="submit" class="btn btn-primary" style="align-self:flex-start;">Envoyer</button>
    </form>
  </div>
</section>

<footer>
  <div class="footer-inner">
    <div class="wordmark" style="font-size:16px;">CORTE<span style="color:var(--coral);">X</span></div>
    <span class="mono">Phase actuelle : collecte de données — construit sur des modèles open source</span>
  </div>
</footer>

<script>
  const sections = [
    {id:'hero', label:'00:00'},
    {id:'about', label:'00:14'},
    {id:'how', label:'00:38'},
    {id:'trust', label:'01:00'},
    {id:'stack', label:'01:20'},
    {id:'wanted', label:'01:45'},
    {id:'contact', label:'02:05'}
  ];
  const track = document.getElementById('track');
  const trackFill = document.getElementById('trackFill');
  const playhead = document.getElementById('playhead');
  const timecode = document.getElementById('timecode');

  function layoutMarkers(){
    document.querySelectorAll('.marker').forEach(m => m.remove());
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    sections.forEach(s => {
      const el = document.getElementById(s.id);
      if(!el) return;
      const pct = Math.min(100, (el.offsetTop / docHeight) * 100);
      const m = document.createElement('div');
      m.className = 'marker';
      m.style.left = pct + '%';
      m.dataset.id = s.id;
      m.addEventListener('click', () => el.scrollIntoView({behavior:'smooth'}));
      track.appendChild(m);
    });
  }

  function fmt(totalSeconds){
    const m = Math.floor(totalSeconds/60).toString().padStart(2,'0');
    const s = Math.floor(totalSeconds%60).toString().padStart(2,'0');
    return m+':'+s;
  }

  function onScroll(){
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const pct = docHeight > 0 ? (window.scrollY / docHeight) * 100 : 0;
    trackFill.style.width = pct + '%';
    playhead.style.left = pct + '%';
    timecode.textContent = fmt(pct/100 * 145);

    let activeId = sections[0].id;
    sections.forEach(s => {
      const el = document.getElementById(s.id);
      if(el && window.scrollY + 100 >= el.offsetTop) activeId = s.id;
    });
    document.querySelectorAll('.marker').forEach(m => {
      m.classList.toggle('active', m.dataset.id === activeId);
    });
  }

  window.addEventListener('load', () => { layoutMarkers(); onScroll(); });
  window.addEventListener('resize', layoutMarkers);
  window.addEventListener('scroll', onScroll);

  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => { if(e.isIntersecting) e.target.classList.add('in'); });
  }, {threshold:0.15});
  document.querySelectorAll('.reveal').forEach(el => io.observe(el));
</script>

</body>
</html>
