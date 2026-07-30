"use strict";

document.addEventListener("DOMContentLoaded", function () {
    initializeNavigation();
    initializeFlashMessages();
    initializeDeleteConfirmations();
    initializeMeasurementRows();
    initializeFormSubmission();
});

function initializeNavigation() {
    const navigationButton = document.querySelector(".nav-toggle");
    const navigationLinks = document.querySelector(".nav-links");

    if (!navigationButton || !navigationLinks) {
        return;
    }

    navigationButton.addEventListener("click", function () {
        navigationLinks.classList.toggle("open");

        const isOpen = navigationLinks.classList.contains("open");

        navigationButton.setAttribute(
            "aria-expanded",
            isOpen ? "true" : "false"
        );
    });
}

function initializeFlashMessages() {
    const closeButtons = document.querySelectorAll(".flash-close");

    closeButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            const message = button.closest(".flash-message");

            if (message) {
                message.remove();
            }
        });
    });
}

function initializeDeleteConfirmations() {
    const deleteForms = document.querySelectorAll(
        "form[data-confirm-delete]"
    );

    deleteForms.forEach(function (form) {
        form.addEventListener("submit", function (event) {
            const customMessage = form.dataset.confirmDelete;

            const message =
                customMessage ||
                "Are you sure you want to delete this item?";

            const confirmed = window.confirm(message);

            if (!confirmed) {
                event.preventDefault();
            }
        });
    });
}

function initializeMeasurementRows() {
    const measurementList = document.querySelector("#measurement-list");
    const addButton = document.querySelector("#add-measurement");

    if (!measurementList || !addButton) {
        return;
    }

    addButton.addEventListener("click", function () {
        addMeasurementRow(measurementList);
    });

    measurementList.addEventListener("click", function (event) {
        const removeButton = event.target.closest(
            ".remove-measurement"
        );

        if (!removeButton) {
            return;
        }

        removeMeasurementRow(measurementList, removeButton);
    });

    updateMeasurementRows(measurementList);
}


function addMeasurementRow(measurementList) {
    const row = document.createElement("div");

    row.className = "measurement-row";

    row.innerHTML = `
        <div class="form-group">
            <label>
                Concentration (mM)
            </label>

            <input
                type="number"
                name="concentrations"
                min="0"
                step="any"
                required
            >
        </div>

        <div class="form-group">
            <label>
                T1 (ms)
            </label>

            <input
                type="number"
                name="t1_values"
                min="0.000001"
                step="any"
                required
            >
        </div>

        <button
            type="button"
            class="button button-danger button-small remove-measurement"
        >
            Remove
        </button>
    `;

    measurementList.appendChild(row);

    updateMeasurementRows(measurementList);

    const firstInput = row.querySelector("input");

    if (firstInput) {
        firstInput.focus();
    }
}


function removeMeasurementRow(measurementList, removeButton) {
    const rows = measurementList.querySelectorAll(
        ".measurement-row"
    );

    if (rows.length <= 2) {
        window.alert(
            "At least two measurements are required for regression."
        );

        return;
    }

    const row = removeButton.closest(".measurement-row");

    if (row) {
        row.remove();
    }

    updateMeasurementRows(measurementList);
}


function updateMeasurementRows(measurementList) {
    const rows = measurementList.querySelectorAll(
        ".measurement-row"
    );

    rows.forEach(function (row, index) {
        let numberLabel = row.querySelector(".row-number");

        if (!numberLabel) {
            numberLabel = document.createElement("span");
            numberLabel.className = "row-number";

            row.prepend(numberLabel);
        }

        numberLabel.textContent = `Measurement ${index + 1}`;
    });

    const removeButtons = measurementList.querySelectorAll(
        ".remove-measurement"
    );

    removeButtons.forEach(function (button) {
        button.disabled = rows.length <= 2;
    });
}

function initializeFormSubmission() {
    const forms = document.querySelectorAll(
        "form[data-disable-on-submit]"
    );

    forms.forEach(function (form) {
        form.addEventListener("submit", function () {
            const submitButton = form.querySelector(
                'button[type="submit"], input[type="submit"]'
            );

            if (!submitButton) {
                return;
            }

            submitButton.disabled = true;

            if (submitButton.tagName === "BUTTON") {
                submitButton.dataset.originalText =
                    submitButton.textContent;

                submitButton.textContent = "Processing...";
            } else {
                submitButton.dataset.originalText =
                    submitButton.value;

                submitButton.value = "Processing...";
            }
        });
    });
}
document.addEventListener("DOMContentLoaded", function () {
    const addButton = document.getElementById("add-measurement");
    const rowsContainer = document.getElementById("measurement-rows");

    if (!addButton || !rowsContainer) {
        return;
    }

    addButton.addEventListener("click", function () {
        const row = document.createElement("div");
        row.classList.add("measurement-row");

        row.innerHTML = `
            <input
                type="number"
                name="concentration"
                step="any"
                placeholder="Concentration (mM)"
                required
            >

            <input
                type="number"
                name="t1"
                step="any"
                placeholder="T1 (ms)"
                required
            >

            <button type="button" class="remove-measurement">
                Remove
            </button>
        `;

        rowsContainer.appendChild(row);
    });

    rowsContainer.addEventListener("click", function (event) {
        if (event.target.classList.contains("remove-measurement")) {
            event.target.closest(".measurement-row").remove();
        }
    });
});
