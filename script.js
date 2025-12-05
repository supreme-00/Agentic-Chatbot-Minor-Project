document.getElementById('login-form').addEventListener('submit', function(event) {
    event.preventDefault();

    const enrollment = document.getElementById('enrollment').value.trim();
    const password = document.getElementById('password').value.trim();

    // Required value
    const requiredValue = "22012011105";

    if (enrollment === requiredValue && password === requiredValue) {
        // Redirect to the chatbot page
        window.location.href = 'chatbot.html';
    } else {
        alert('Invalid enrollment or password. Both must be 22012011105.');
    }
});

// Lost password link
document.querySelector('.lost-password').addEventListener('click', function(event) {
    event.preventDefault();
    alert('Redirecting to the password recovery page...');
});
