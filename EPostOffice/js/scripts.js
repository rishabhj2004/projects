document.addEventListener('DOMContentLoaded', function () {
    // Toggle to show login form
    document.getElementById('show-login').addEventListener('click', function (event) {
        event.preventDefault();
        document.getElementById('login-form').style.display = 'block';
        document.getElementById('register-form').style.display = 'none';
    });

    // Toggle to show register form
    document.getElementById('show-register').addEventListener('click', function (event) {
        event.preventDefault();
        document.getElementById('register-form').style.display = 'block';
        document.getElementById('login-form').style.display = 'none';
    });

    // Handle login form submission
    document.getElementById('login-form-action').addEventListener('submit', function (event) {
        event.preventDefault();
        // Mock login
        alert('Login successful!');
        window.location.href = 'home.html';  // Redirect to home page after login
    });

    // Handle register form submission
    document.getElementById('register-form-action').addEventListener('submit', function (event) {
        event.preventDefault();
        // Mock registration
        alert('Registration successful!');
        window.location.href = 'home.html';  // Redirect to home page after registration
    });
});
