async function fetchEvents() {
    const response = await fetch("/api/events");
    const events = await response.json();
    const container = document.getElementById("events-container");
    container.innerHTML = "";

    events.forEach(event => {
        let message;
        if (event.action === "PUSH") {
            message = `${event.author} pushed to ${event.to_branch} on ${event.timestamp}`;
        } else if (event.action === "PULL_REQUEST") {
            message = `${event.author} submitted a pull request from ${event.from_branch} to ${event.to_branch} on ${event.timestamp}`;
        } else if (event.action === "MERGE") {
            message = `${event.author} merged ${event.from_branch} into ${event.to_branch} on ${event.timestamp}`;
        }

        const eventElement = document.createElement("div");
        eventElement.className = "event";
        eventElement.textContent = message;
        container.appendChild(eventElement);
    });
}

// Poll every 15 seconds
setInterval(fetchEvents, 15000);
fetchEvents();  // Initial load
