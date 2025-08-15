document.getElementById('contact-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = {
        name: document.getElementById('name').value,
        email: document.getElementById('email').value,
        subject: document.getElementById('subject').value,
        message: document.getElementById('message').value
    };

    try {
        const response = await fetch('http://localhost:5000/api/contact', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        if (response.ok) {
            alert('Contact form submitted successfully!');
            this.reset();
        } else {
            alert(result.error || 'Failed to submit contact form');
        }
    } catch (error) {
        alert('Error submitting contact form: ' + error.message);
    }
});