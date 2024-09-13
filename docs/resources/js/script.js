// utilities
var get = function (selector, scope) {
  scope = scope ? scope : document;
  return scope.querySelector(selector);
};

var getAll = function (selector, scope) {
  scope = scope ? scope : document;
  return scope.querySelectorAll(selector);
};

//in-page scrolling for documentation page
var btns = getAll('.js-btn');
var sections = getAll('.js-section');

function setActiveLink(index) {
  // remove all active tab classes
  for (var i = 0; i < btns.length; i++) {
    btns[i].classList.remove('selected');
  }

  // add active class to the current section
  btns[index].classList.add('selected');
}

function smoothScrollTo(i, event) {
  var element = sections[i];
  setActiveLink(i);

  window.scrollTo({
    behavior: 'smooth',
    top: element.offsetTop - 20,
    left: 0
  });

  event.preventDefault();
}

if (btns.length && sections.length > 0) {
  for (var i = 0; i < btns.length; i++) {
    btns[i].addEventListener('click', smoothScrollTo.bind(this, i));
  }
}

// fix menu to page-top once user starts scrolling
window.addEventListener('scroll', function () {
  var docNav = get('.doc__nav > ul');
  
  if (docNav) {
    if (window.pageYOffset > 63) {
      docNav.classList.add('fixed');
    } else {
      docNav.classList.remove('fixed');
    }
  }

  // Highlight menu item based on scroll position
  var currentPosition = window.pageYOffset;
  sections.forEach(function (section, index) {
    if (currentPosition >= section.offsetTop - 100 && currentPosition < section.offsetTop + section.offsetHeight) {
      setActiveLink(index);
    }
  });
});

// responsive navigation
var topNav = get('.menu');
var icon = get('.toggle');

window.addEventListener('load', function () {
  function showNav() {
    if (topNav.className === 'menu') {
      topNav.className += ' responsive';
      icon.className += ' open';
    } else {
      topNav.className = 'menu';
      icon.classList.remove('open');
    }
  }
  icon.addEventListener('click', showNav);
});
