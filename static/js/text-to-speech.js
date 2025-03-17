class TextToSpeech {
    constructor() {
        this.synth = window.speechSynthesis;
        this.speaking = false;
    }

    speak(text) {
        if (this.speaking) {
            this.stop();
            return;
        }

        if (text) {
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 1;
            utterance.pitch = 1;
            utterance.onend = () => {
                this.speaking = false;
                this.updateButtons();
            };
            this.speaking = true;
            this.updateButtons();
            this.synth.speak(utterance);
        }
    }

    stop() {
        this.synth.cancel();
        this.speaking = false;
        this.updateButtons();
    }

    updateButtons() {
        const buttons = document.querySelectorAll('.speak-button');
        buttons.forEach(button => {
            button.textContent = this.speaking ? '🔊 Stop' : '🔊 Read';
            button.setAttribute('aria-label', this.speaking ? 'Stop reading' : 'Read text');
        });
    }
}

// Initialize TTS when document is loaded
document.addEventListener('DOMContentLoaded', () => {
    const tts = new TextToSpeech();

    // Product Details Speech
    const productDetailsBtn = document.getElementById('speak-product-details');
    if (productDetailsBtn) {
        productDetailsBtn.addEventListener('click', () => {
            const productDetails = document.querySelector('.product-details-content');
            if (productDetails) {
                tts.speak(productDetails.textContent);
            }
        });
    }

    // Cultivation Method Speech
    const cultivationDetailsBtn = document.getElementById('speak-cultivation-details');
    if (cultivationDetailsBtn) {
        cultivationDetailsBtn.addEventListener('click', () => {
            const cultivationDetails = document.querySelector('.cultivation-method');
            if (cultivationDetails) {
                tts.speak(cultivationDetails.textContent);
            }
        });
    }
}); 