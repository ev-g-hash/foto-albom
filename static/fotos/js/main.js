document.addEventListener('DOMContentLoaded', () => {
  // Лёгкая печать текста на главной
  const typedEl = document.getElementById('typed');
  if (typedEl) {
    const text = 'Пусть этот год принесёт яркие впечатления, крепкое здоровье и много радостных моментов!';
    let i = 0;
    const timer = setInterval(() => {
      typedEl.textContent += text[i];
      i++;
      if (i >= text.length) clearInterval(timer);
    }, 30);
  }

  // Конфетти на главной (Canvas)
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

    const colors = ['#f59e0b', '#60a5fa', '#34d399', '#f472b6', '#a78bfa'];
    const pieces = Array.from({ length: 120 }, () => ({
      x: Math.random() * window.innerWidth,
      y: -10 - Math.random() * 200,
      w: 6 + Math.random() * 6,
      h: 10 + Math.random() * 14,
      tilt: Math.random() * 2 * Math.PI,
      tiltSpeed: 0.02 + Math.random() * 0.06,
      speed: 1 + Math.random() * 2.5,
      color: colors[Math.floor(Math.random() * colors.length)],
      opacity: 0.8 + Math.random() * 0.2
    }));

    function tick() {
      ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);
      for (const p of pieces) {
        p.y += p.speed;
        p.tilt += p.tiltSpeed;
        const x = p.x + Math.sin(p.tilt) * 8;
        const y = p.y;
        ctx.globalAlpha = p.opacity;
        ctx.fillStyle = p.color;
        ctx.fillRect(x, y, p.w, p.h);
        if (y > window.innerHeight + 20) {
          p.y = -10;
          p.x = Math.random() * window.innerWidth;
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