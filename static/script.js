// Password visibility toggle
function togglePassword(inputId, button) {
	const input = document.getElementById(inputId);
	const icon = document.getElementById(inputId + '-icon');
	if (input.type === 'password') {
		input.type = 'text';
		icon.classList.remove('bi-eye');
		icon.classList.add('bi-eye-slash');
	} else {
		input.type = 'password';
		icon.classList.remove('bi-eye-slash');
		icon.classList.add('bi-eye');
	}
}

// Validate password match in change password form
function validatePasswordMatch() {
	const newPassword = document.getElementById('newPassword');
	const confirmPassword = document.getElementById('confirmPassword');
	const errorDiv = document.getElementById('passwordMatchError');
	
	if (newPassword && confirmPassword && errorDiv) {
		if (confirmPassword.value && newPassword.value !== confirmPassword.value) {
			errorDiv.style.display = 'block';
			confirmPassword.setCustomValidity('Passwords do not match');
		} else {
			errorDiv.style.display = 'none';
			confirmPassword.setCustomValidity('');
		}
	}
}

document.addEventListener('DOMContentLoaded', () => {
	// Apply widths for any progress bars using data-width to avoid inline Jinja in CSS
	document.querySelectorAll('.js-width[data-width]')
		.forEach(el => {
			const w = parseFloat(el.getAttribute('data-width')) || 0;
			el.style.width = `${Math.max(0, Math.min(100, w))}%`;
		});

	// Default date field to today if empty
	const dateInputs = document.querySelectorAll('input[type="date"][name="date"]');
	const today = new Date();
	const yyyy = today.getFullYear();
	const mm = String(today.getMonth() + 1).padStart(2, '0');
	const dd = String(today.getDate()).padStart(2, '0');
	const todayStr = `${yyyy}-${mm}-${dd}`;
	dateInputs.forEach(input => {
		if (!input.value) input.value = todayStr;
	});
});
