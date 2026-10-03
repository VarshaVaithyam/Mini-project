const navItems = document.querySelectorAll('.nav-item');
const views = document.querySelectorAll('.view');
const pageTitle = document.getElementById('pageTitle');
const toast = document.getElementById('toast');
let stream = null;

function notify(message) {
  toast.textContent = message;
  toast.classList.add('show');
  clearTimeout(window.toastTimer);
  window.toastTimer = setTimeout(() => toast.classList.remove('show'), 3000);
}
function showView(name) {
  navItems.forEach(item => item.classList.toggle('active', item.dataset.view === name));
  views.forEach(view => view.classList.toggle('active-view', view.id === `view-${name}`));
  const label = document.querySelector(`[data-view="${name}"]`).textContent.trim().replace('●','').trim();
  pageTitle.textContent = label;
  window.scrollTo({top:0, behavior:'smooth'});
}
navItems.forEach(item => item.addEventListener('click', () => showView(item.dataset.view)));

document.getElementById('startSession').addEventListener('click', () => {
  showView('monitor');
  notify('Session started — monitoring your signals');
});
document.getElementById('historyBtn').addEventListener('click', () => showView('history'));
document.getElementById('viewAll').addEventListener('click', () => notify('You have 4 personalized resets available'));

document.getElementById('beginBreathing').addEventListener('click', () => document.getElementById('breathingModal').classList.add('open'));
document.getElementById('closeModal').addEventListener('click', () => document.getElementById('breathingModal').classList.remove('open'));
document.getElementById('finishBreath').addEventListener('click', () => {
  document.getElementById('breathingModal').classList.remove('open');
  const score = document.getElementById('scoreValue');
  score.textContent = '20';
  notify('Nice work — your reset was logged');
});
document.getElementById('breathingModal').addEventListener('click', e => {
  if (e.target.id === 'breathingModal') e.currentTarget.classList.remove('open');
});

const cameraToggle = document.getElementById('cameraToggle');
const cameraBox = document.getElementById('cameraBox');
const webcam = document.getElementById('webcam');
cameraToggle.addEventListener('click', async () => {
  if (stream) {
    stream.getTracks().forEach(track => track.stop());
    stream = null;
    cameraBox.classList.remove('on');
    cameraToggle.textContent = 'Start camera monitoring';
    notify('Camera monitoring paused');
    return;
  }
  try {
    stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
    webcam.srcObject = stream;
    cameraBox.classList.add('on');
    cameraToggle.textContent = 'Pause camera monitoring';
    notify('Camera connected — signals are being analyzed locally');
  } catch (error) {
    // A graceful demo fallback keeps the dashboard usable when camera permission is unavailable.
    cameraBox.classList.add('on');
    cameraToggle.textContent = 'Pause camera monitoring';
    notify('Demo monitoring active — camera access was not available');
  }
});

document.querySelector('.date-btn').addEventListener('click', () => notify('Showing data for Friday, October 3'));
document.querySelector('.icon-btn').addEventListener('click', () => notify('You’re all caught up'));

document.addEventListener('keydown', e => {
  if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
    e.preventDefault();
    showView('settings');
  }
});
// Small live-signal simulation while monitoring is active.
setInterval(() => {
  if (!stream && !cameraBox.classList.contains('on')) return;
  const blink = 15 + Math.floor(Math.random() * 5);
  document.getElementById('liveBlink').textContent = `${blink} bpm`;
}, 4000);
