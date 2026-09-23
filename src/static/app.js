document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  function showMessage(text, type) {
    messageDiv.textContent = text;
    messageDiv.className = type;
    messageDiv.classList.remove("hidden");

    setTimeout(() => {
      messageDiv.classList.add("hidden");
    }, 5000);
  }

  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      activitiesList.innerHTML = "";
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;
        const participants = details.participants && details.participants.length
          ? details.participants
              .map(
                (email) => `
                  <li class="participant-item">
                    <span class="participant-email">${email}</span>
                    <button
                      type="button"
                      class="participant-remove"
                      data-activity="${name}"
                      data-email="${email}"
                      aria-label="Remove ${email} from ${name}"
                      title="Unregister ${email}"
                    >
                      ✕
                    </button>
                  </li>`
              )
              .join("")
          : "<li class='participant-empty'>No participants yet.</li>";

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants-block">
            <p><strong>Participants:</strong></p>
            <ul class="participants-list">
              ${participants}
            </ul>
          </div>
        `;

        activitiesList.appendChild(activityCard);

        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });

      document.querySelectorAll(".participant-remove").forEach((button) => {
        button.addEventListener("click", async () => {
          const { activity, email } = button.dataset;

          try {
            const response = await fetch(
              `/activities/${encodeURIComponent(activity)}/unregister?email=${encodeURIComponent(email)}`,
              {
                method: "DELETE",
              }
            );

            const result = await response.json();

            if (response.ok) {
              showMessage(result.message, "success");
              await fetchActivities();
            } else {
              showMessage(result.detail || "Could not unregister the participant.", "error");
            }
          } catch (error) {
            console.error("Error unregistering participant:", error);
            showMessage("Failed to unregister participant.", "error");
          }
        });
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        showMessage(result.message, "success");
        signupForm.reset();
        await fetchActivities();
      } else {
        showMessage(result.detail || "An error occurred", "error");
      }
    } catch (error) {
      showMessage("Failed to sign up. Please try again.", "error");
      console.error("Error signing up:", error);
    }
  });

  fetchActivities();
});
