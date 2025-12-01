// ----------------------------------------
// Prikaz predloženih pitanja u #suggestions
// ----------------------------------------
function renderSuggestions(suggestions) {
    const container = document.getElementById("suggestions");
    container.innerHTML = "";

    if (!suggestions || suggestions.length === 0) return;

    suggestions.forEach(q => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "suggestion-btn";
        btn.textContent = q;

        btn.addEventListener("click", () => {
            const input = document.getElementById("user-input");
            input.value = q;
            sendMessage();
        });

        container.appendChild(btn);
    });
}

// ----------------------------------------
// SLANJE PORUKE BOTU
// ----------------------------------------
async function sendMessage() {
    const input = document.getElementById("user-input");
    const chat = document.getElementById("chat-window");
    const userText = input.value.trim();

    if (!userText) return;

    // --- poruka korisnika ---
    const userMsg = document.createElement("div");
    userMsg.className = "message user";
    userMsg.textContent = userText;
    chat.appendChild(userMsg);

    input.value = "";
    chat.scrollTop = chat.scrollHeight;

    // --- bot typing mehurić ---
    const typingBubble = document.createElement("div");
    typingBubble.className = "typing";
    typingBubble.innerHTML = `
        <span class="dots">
            <span></span><span></span><span></span>
        </span>
    `;
    chat.appendChild(typingBubble);
    chat.scrollTop = chat.scrollHeight;

    try {
        // 🔥 OBAVEZNO ZA SLANJE SESSION COOKIEJA
        const response = await fetch("/api/message", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",   // 🔥 KLJUČNO
            body: JSON.stringify({ message: userText })
        });

        const data = await response.json();

        // mali delay radi animacije
        await new Promise(resolve => setTimeout(resolve, 600));

        // ukloni bubble
        typingBubble.remove();

        // --- poruka bota ---
        const botMsg = document.createElement("div");
        botMsg.className = "message bot";
        botMsg.textContent = data.answer;
        chat.appendChild(botMsg);
        chat.scrollTop = chat.scrollHeight;

        // --- predložena pitanja ---
        if (data.suggestions) {
            renderSuggestions(data.suggestions);
        }

    } catch (err) {
        typingBubble.remove();

        const errorMsg = document.createElement("div");
        errorMsg.className = "message bot";
        errorMsg.textContent = "Došlo je do greške. Pokušaj ponovo kasnije.";
        chat.appendChild(errorMsg);
        chat.scrollTop = chat.scrollHeight;

        console.error(err);
    }
}

// ----------------------------------------
// submit forme
// ----------------------------------------
document.getElementById("chat-form").addEventListener("submit", function (e) {
    e.preventDefault();
    sendMessage();
});

// ----------------------------------------
// Enter u input polju
// ----------------------------------------
document.getElementById("user-input").addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
        e.preventDefault();
        sendMessage();
    }
});
