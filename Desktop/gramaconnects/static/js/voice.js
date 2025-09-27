// static/js/voice.js

let selectedLanguage = 'en';  // Default is English

function speak(text) {
    const utterance = new SpeechSynthesisUtterance(text);

    // Set language based on selected
    if (selectedLanguage === 'ta') {
        utterance.lang = 'ta-IN';  // Tamil
    } else {
        utterance.lang = 'en-US';  // English
    }

    window.speechSynthesis.speak(utterance);
}

// Call this when page loads
function greetUser() {
    if (selectedLanguage === 'ta') {
        speak("வணக்கம்! கிராமா கனெக்ட் செயலிக்கு வரவேற்கிறோம்");
    } else {
        speak("Welcome to Grama Connect web app. Empowering rural talent.");
    }
}

// Voice feedback on button click
function addVoiceToButtons() {
    const buttons = document.querySelectorAll('button');
    buttons.forEach((btn) => {
        btn.addEventListener('click', () => {
            let label = btn.innerText || btn.getAttribute('aria-label') || "Action performed";

            if (selectedLanguage === 'ta') {
                speak("நீங்கள் தேர்ந்தெடுத்த செயலி: " + label);
            } else {
                speak("You selected: " + label);
            }
        });
    });
}

// Set language dynamically
function setLanguage(langCode) {
    selectedLanguage = langCode;
    greetUser();
}