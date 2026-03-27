console.log("SCRIPT LOADED");

document.addEventListener("DOMContentLoaded", () => {

  // 1) カードを順番に表示
  const cards = document.querySelectorAll(".card");

  cards.forEach((card, index) => {
    card.style.opacity = "0";
    card.style.transform = "translateY(18px) scale(0.98)";

    setTimeout(() => {
      card.style.transition = "opacity 0.55s ease, transform 0.55s ease";
      card.style.opacity = "1";
      card.style.transform = "translateY(0) scale(1)";
    }, index * 140);
  });

  // 2) タロット画像登場演出
  const tarotImage = document.querySelector(".tarot-image");

  if (tarotImage) {
    tarotImage.style.opacity = "0";
    tarotImage.style.transform = "rotate(-3deg) scale(0.94)";

    setTimeout(() => {
      tarotImage.style.transition = "opacity 0.7s ease, transform 0.7s ease";
      tarotImage.style.opacity = "1";
      tarotImage.style.transform = "rotate(0deg) scale(1)";
    }, 350);
  }

  // 3) ボタン押下演出
  const submitButton = document.querySelector('button[type="submit"]');

  if (submitButton) {
    submitButton.addEventListener("mousedown", () => {
      submitButton.style.transform = "scale(0.98)";
    });

    submitButton.addEventListener("mouseup", () => {
      submitButton.style.transform = "scale(1)";
    });

    submitButton.addEventListener("mouseleave", () => {
      submitButton.style.transform = "scale(1)";
    });
  }

  // 4) 螺旋キラキラ生成
  function spawnSpiralSparkles(tarotCard){

    const layer = tarotCard.querySelector(".sparkle-layer");
    if(!layer) return;

    layer.innerHTML = "";

    const symbols = ["✦","✧","☾","☆","✦"];
    const count = 20;

    const rise = 240;

    for(let i=0;i<count;i++){

      const spark = document.createElement("span");
      spark.className = "spark";
      spark.textContent = symbols[i % symbols.length];

      spark.style.fontSize = `${16 + (i%3)*3}px`;

      layer.appendChild(spark);

    const delay = i*90;
      const duration = 2200;

      const start = performance.now()+delay;
      const end = start+duration;

      const offset = 1;

      function move(now){

        if(now < start){
          requestAnimationFrame(move);
          return;
        }

        if(now > end){
          spark.remove();
          return;
        }

        const t = (now-start)/duration;

        const spiralScale = 1.6;

        const y = -t*rise*spiralScale;

        // ここがポイント（横ゆらぎ）
        const x = Math.sin(t*4 + i*0.6)*60*spiralScale*offset;

        const scale = 0.35 + t*0.9;

        spark.style.transform =
          `translate(-50%, -50%) translate(${x}px, ${y}px) scale(${scale})`;

        if(t < 0.15){
          spark.style.opacity = t/0.15;
        }
        else if(t > 0.8){
          spark.style.opacity = (1-t)/0.2;
        }
        else{
          spark.style.opacity = 1;
        }

        requestAnimationFrame(move);
      }

      requestAnimationFrame(move);
    }

  }

  // 5) タロットカードめくり
  const tarotCard = document.getElementById("tarotCard");

  if (tarotCard) {
    let isAnimating = false;

    tarotCard.addEventListener("click", () => {
      if (isAnimating) return;

      isAnimating = true;

      tarotCard.classList.add("glow");
      spawnSpiralSparkles(tarotCard);

      setTimeout(() => {
        tarotCard.classList.toggle("flip");
      }, 1100);

      setTimeout(() => {
        tarotCard.classList.remove("glow");
        isAnimating = false;
      }, 2200);
    });
  }

});