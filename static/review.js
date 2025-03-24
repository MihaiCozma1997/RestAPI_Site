// Get all the star elements
const stars = document.querySelectorAll('.star-rating-inner i');
const reviewRatingInput = document.getElementById('review-rating');
const comment = document.getElementById("review-comment");

// Get the close button and submit review button
const closeButton = document.querySelector('.close-btn');
const submitButton = document.getElementById('submit-review');

// Function to reset the star rating (clear previous hover/selected states)
function resetStars() {
    stars.forEach(star => {
        star.classList.remove('selected', 'hovered');
    });
    reviewRatingInput.value = '';
    comment.value = '';
}

// Add event listener to each star for the click event
stars.forEach(star => {
    star.addEventListener('click', function() {
        const rating = parseInt(star.getAttribute('data-value')); // Get the value of the clicked star
        reviewRatingInput.value = rating; // Set the value in the hidden input

        // Update the stars' appearance based on the selected rating
        updateStars(rating);
    });

    // Add hover effect to each star
    star.addEventListener('mouseover', function() {
        const rating = parseInt(star.getAttribute('data-value'));
        updateStarsHover(rating);
    });

    // Reset hover effect when the mouse leaves
    star.addEventListener('mouseout', function() {
        const currentRating = parseInt(reviewRatingInput.value) || 0;
        updateStarsHover(currentRating); // Restore the hover effect based on the current rating
    });
});

// Function to update stars based on the rating (selected state)
function updateStars(rating) {
    stars.forEach((star, index) => {
        // If the index is less than the rating, mark it as selected
        if (index < rating) {
            star.classList.add('selected');
        } else {
            star.classList.remove('selected');
        }
    });
}

// Function to temporarily update the stars on hover (hover effect)
function updateStarsHover(rating) {
    stars.forEach((star, index) => {
        // If the index is less than the rating, highlight it (hover effect)
        if (index < rating) {
            star.classList.add('hovered');
        } else {
            star.classList.remove('hovered');
        }
    });
}

// Optional: Pre-select the stars based on the existing rating (if available)
if (reviewRatingInput.value) {
    updateStars(parseInt(reviewRatingInput.value)); // Pre-select stars based on existing rating
}

// Event listener for the close button to reset stars
closeButton.addEventListener('click', function() {
    resetStars(); // Reset the stars when the close button is clicked
});
