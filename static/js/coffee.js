// scripts.js

// Add any interactive behavior here
// For example, smooth scrolling to sections on clicking links
const navLinks = document.querySelectorAll('nav a');

navLinks.forEach(link => {
  link.addEventListener('click', e => {
    e.preventDefault();
    const target = document.querySelector(e.target.getAttribute('href'));
    target.scrollIntoView({ behavior: 'smooth' });
  });
});


// Toggle the responsive navigation menu
const menuButton = document.querySelector('.menu-toggle');
const navList = document.querySelector('.nav-list');

menuButton.addEventListener('click', () => {
  navList.classList.toggle('show');
});

