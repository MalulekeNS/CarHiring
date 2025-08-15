document.getElementById('booking-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = {
        full_name: document.getElementById('full_name').value,
        email: document.getElementById('email').value,
        phone: document.getElementById('phone').value,
        vehicle: document.getElementById('vehicle').value,
        pickup_date: document.getElementById('pickup_date').value,
        return_date: document.getElementById('return_date').value,
        additional_requests: document.getElementById('additional_requests').value,
        payment_method: document.getElementById('payment_method').value
    };

    try {
        const response = await fetch('http://localhost:5000/api/bookings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        if (response.ok) {
            alert('Booking submitted successfully!');
            this.reset();
        } else {
            alert(result.error || 'Failed to submit booking');
        }
    } catch (error) {
        alert('Error submitting booking: ' + error.message);
    }
});