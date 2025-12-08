document.addEventListener('DOMContentLoaded', () => {
  // Лёгкая печать текста на главной
  const typedEl = document.getElementById('typed');
  if (typedEl) {
    const text = 'Коллекция самых дорогих и незабываемых моментов, сохранённых в этом цифровом альбоме. Пусть каждая фотография напоминает о прекрасных мгновениях жизни!';
    let i = 0;
    const timer = setInterval(() => {
      typedEl.textContent += text[i];
      i++;
      if (i >= text.length) clearInterval(timer);
    }, 30);
  }

  // Конфетти на главной (Canvas) - улучшенное
  const confettiCanvas = document.getElementById('confetti');
  if (confettiCanvas) {
    const ctx = confettiCanvas.getContext('2d');
    const DPR = window.devicePixelRatio || 1;
    const resize = () => {
      confettiCanvas.width = window.innerWidth * DPR;
      confettiCanvas.height = window.innerHeight * DPR;
      ctx.scale(DPR, DPR);
    };
    resize();
    window.addEventListener('resize', resize);

    const colors = ['#ffd700', '#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57', '#ff9ff3', '#54a0ff'];
    const pieces = Array.from({ length: 150 }, () => ({
      x: Math.random() * window.innerWidth,
      y: -10 - Math.random() * 200,
      w: 6 + Math.random() * 8,
      h: 10 + Math.random() * 16,
      tilt: Math.random() * 2 * Math.PI,
      tiltSpeed: 0.02 + Math.random() * 0.08,
      speed: 1 + Math.random() * 3,
      color: colors[Math.floor(Math.random() * colors.length)],
      opacity: 0.8 + Math.random() * 0.2,
      rotation: Math.random() * 360,
      rotationSpeed: (Math.random() - 0.5) * 4
    }));

    function tick() {
      ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);
      for (const p of pieces) {
        p.y += p.speed;
        p.tilt += p.tiltSpeed;
        p.rotation += p.rotationSpeed;
        const x = p.x + Math.sin(p.tilt) * 10;
        const y = p.y;
        
        ctx.save();
        ctx.globalAlpha = p.opacity;
        ctx.translate(x + p.w/2, y + p.h/2);
        ctx.rotate(p.rotation * Math.PI / 180);
        ctx.fillStyle = p.color;
        ctx.fillRect(-p.w/2, -p.h/2, p.w, p.h);
        ctx.restore();
        
        if (y > window.innerHeight + 20) {
          p.y = -10;
          p.x = Math.random() * window.innerWidth;
          p.rotation = Math.random() * 360;
        }
      }
      requestAnimationFrame(tick);
    }
    tick();
  }

  // Лайтбокс для галереи
  const lightbox = document.getElementById('lightbox');
  const lightboxImg = document.getElementById('lightbox-img');
  if (lightbox && lightboxImg) {
    document.addEventListener('click', (e) => {
      const target = e.target;
      if (target && target.matches('.gallery img')) {
        const full = target.getAttribute('data-full') || target.src;
        const title = target.getAttribute('data-title') || '';
        const desc = target.getAttribute('data-desc') || '';
        lightboxImg.src = full;
        lightboxImg.alt = title || desc || 'Увеличенное фото';
        lightbox.classList.add('open');
      }
    });

    lightbox.addEventListener('click', () => {
      lightbox.classList.remove('open');
      lightboxImg.src = '';
    });
  }
});