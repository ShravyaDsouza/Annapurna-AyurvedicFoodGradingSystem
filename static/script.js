// Sticky header functionality
window.onscroll = function () {
    toggleStickyHeader()
};

var header = document.getElementById("header");
var sticky = header.offsetTop;

function toggleStickyHeader() {
    if (window.pageYOffset > sticky) {
        header.classList.add("sticky");
    } else {
        header.classList.remove("sticky");
    }
}

// Handle label and radio button selection
const labels = document.querySelectorAll('label');

// Add event listener for each label
labels.forEach(label => {
    label.addEventListener('click', function () {
        // Get the associated radio button by matching label 'for' attribute
        const radioId = label.getAttribute('for');
        const radioButton = document.getElementById(radioId);

        // Deselect all other radio buttons and labels
        document.querySelectorAll('input[type="radio"]').forEach(radio => radio.checked = false);
        document.querySelectorAll('label').forEach(lbl => lbl.classList.remove('selected'));

        // Select the clicked radio button and highlight the label
        radioButton.checked = true;
        label.classList.add('selected');
    });
});

function nextQuestion(questionNumber) {
    // Get the current visible question element
    const currentQuestion = document.querySelector('.question:not([style*="display: none"])');
    const nextQuestion = document.getElementById(`question${questionNumber}`);

    // Get the selected radio button in the current question
    const selectedOption = currentQuestion.querySelector('input[type="radio"]:checked');

    // Check if a radio option is selected
    if (selectedOption) {
        // Hide the current question
        currentQuestion.style.display = 'none';

        // Show the next question
        if (nextQuestion) {
            nextQuestion.style.display = 'block';
        } else {
            alert('You have reached the end of the quiz.');
        }
    } else {
        // If no option is selected, show an alert
        alert('Please select an option before proceeding.');
    }
}


// Function to move to the previous question
function previousQuestion(prevQuestionNumber) {
    const currentQuestion = document.querySelector('.question:not([style*="display: none"])');
    const prevQuestion = document.getElementById(`question${prevQuestionNumber}`);

    if (currentQuestion) {
        currentQuestion.style.display = 'none';
    }

    if (prevQuestion) {
        prevQuestion.style.display = 'block';
    }
}

// Close the modal
function closeModal() {
    const modal = document.getElementById('submissionModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Handle form submission via JavaScript
document.getElementById('dosha-quiz').addEventListener('submit', function (event) {
    // Prevent default form submission
    event.preventDefault();

    // Display the success message using an alert
    alert('Quiz successfully submitted! Thank you.');
    window.location.href = "/dashboard";
});
document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss flash messages after 5 seconds
    setTimeout(function() {
        const flashMessages = document.getElementById('flash-messages');
        if (flashMessages) {
            flashMessages.style.display = 'none';  // Hide after 5 seconds
        }
    }, 5000);

    // Allow manual closing of flash messages
    const closeButtons = document.querySelectorAll('.close-btn');
    closeButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const alertBox = this.parentElement;  // Close the parent alert
            alertBox.style.display = 'none';
        });
    });
});


