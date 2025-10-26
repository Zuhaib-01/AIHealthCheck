// Rotating health tips
const tips = [
  "Drink at least 2-3 liters of water daily 💧",
  "Aim for 7-8 hours of quality sleep 😴",
  "Stretch for 5 minutes every hour if sitting long 🧘‍♂️",
  "Eat a balanced diet rich in fruits and vegetables 🍎",
  "Limit added sugar and processed foods 🚫",
  "Take short walks after meals for better digestion 🚶‍♀️"
];

const randomTip = tips[Math.floor(Math.random() * tips.length)];
document.getElementById("health-tip").innerText = randomTip;
