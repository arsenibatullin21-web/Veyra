const profilePage = document.querySelector("[data-profile-page]");
const editPanel = document.querySelector("[data-profile-edit-panel]");
const editButton = document.querySelector("[data-profile-edit-button]");
const closeButton = document.querySelector("[data-profile-close-button]");
const cancelButton = document.querySelector("[data-profile-cancel-button]");
const passwordPanel = document.querySelector("[data-password-edit-panel]");
const passwordButton = document.querySelector("[data-password-edit-button]");
const passwordCloseButton = document.querySelector("[data-password-close-button]");
const passwordCancelButton = document.querySelector("[data-password-cancel-button]");

function openEditPanel() {
    if (!editPanel) {
        return;
    }

    editPanel.classList.add("is-open");
    editPanel.scrollIntoView({ behavior: "smooth", block: "start" });
}

function closeEditPanel() {
    if (!editPanel) {
        return;
    }

    editPanel.classList.remove("is-open");
}

function openPasswordPanel() {
    if (!passwordPanel) {
        return;
    }

    passwordPanel.classList.add("is-open");
    passwordPanel.scrollIntoView({ behavior: "smooth", block: "start" });
}

function closePasswordPanel() {
    if (!passwordPanel) {
        return;
    }

    passwordPanel.classList.remove("is-open");
}

if (profilePage && profilePage.dataset.editing === "true") {
    openEditPanel();
}

if (profilePage && profilePage.dataset.passwordEditing === "true") {
    openPasswordPanel();
}

if (editButton) {
    editButton.addEventListener("click", openEditPanel);
}

if (closeButton) {
    closeButton.addEventListener("click", closeEditPanel);
}

if (cancelButton) {
    cancelButton.addEventListener("click", closeEditPanel);
}

if (passwordButton) {
    passwordButton.addEventListener("click", openPasswordPanel);
}

if (passwordCloseButton) {
    passwordCloseButton.addEventListener("click", closePasswordPanel);
}

if (passwordCancelButton) {
    passwordCancelButton.addEventListener("click", closePasswordPanel);
}
