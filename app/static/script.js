let currentInferenceId = null;

document.addEventListener("DOMContentLoaded", () => {
    fetchInference();

    document.getElementById("btn-reject").addEventListener("click", () => handleTriage("reject"));
    document.getElementById("btn-approve").addEventListener("click", () => handleTriage("approve"));
    document.getElementById("btn-edit").addEventListener("click", toggleEdit);
    document.getElementById("btn-submit-edit").addEventListener("click", () => handleTriage("approve", true));
});

async function fetchInference() {
    try {
        const response = await fetch("/api/inference");
        const data = await response.json();

        if (data.message === "No pending inferences") {
            showEmptyState();
            return;
        }

        renderCard(data);
    } catch (error) {
        console.error("Error fetching inference:", error);
    }
}

function renderCard(data) {
    currentInferenceId = data.id;
    document.getElementById("source-badge").textContent = data.source;
    document.getElementById("confidence-badge").textContent = `Conf: ${(data.confidence * 100).toFixed(0)}%`;
    document.getElementById("inference-text").textContent = data.inference;
    document.getElementById("content-text").textContent = data.content;

    // Reset edit state
    document.getElementById("edit-section").classList.add("hidden");
    document.getElementById("edit-notes").value = "";
}

function showEmptyState() {
    document.getElementById("inference-card").classList.add("hidden");
    document.getElementById("empty-state").classList.remove("hidden");
}

function toggleEdit() {
    const editSection = document.getElementById("edit-section");
    editSection.classList.toggle("hidden");
}

async function handleTriage(action, withNotes = false) {
    if (!currentInferenceId) return;

    let notes = null;
    if (withNotes) {
        notes = document.getElementById("edit-notes").value;
    }

    try {
        const response = await fetch("/api/triage", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                id: currentInferenceId,
                action: action,
                notes: notes
            })
        });

        if (response.ok) {
            fetchInference(); // Load next
        } else {
            alert("Error submitting decision");
        }
    } catch (error) {
        console.error("Error submitting triage:", error);
    }
}
