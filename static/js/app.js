
document.addEventListener("DOMContentLoaded", () => {

    const form = document.getElementById("upload_form");
    const msgDiv = document.getElementById("message");
    const tbody = document.getElementById("report_table_body");
    const fileInput = document.getElementById("word_file");
    const patientInput = document.getElementById("patient_name");

    /* ===============================
       AUTO PATIENT NAME FROM FILE
    =============================== */
    fileInput.addEventListener("change", () => {
        if (fileInput.files.length > 0) {
            let name = fileInput.files[0].name;
            name = name.replace(".docx", "").replace(/_/g, " ");
            patientInput.value = name;
        }
    });

    /* ===============================
       FETCH TODAY REPORTS
    =============================== */
    window.fetchTodayReports = async function () {
        try {
            const res = await fetch("/get_today_reports");
            if (!res.ok) throw new Error("Fetch failed");

            const data = await res.json();
            tbody.innerHTML = "";

            if (!data.length) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="5" class="text-center text-muted">
                            No reports found
                        </td>
                    </tr>`;
                return;
            }

            data.forEach((row, index) => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td>${index + 1}</td>
                    <td>${row.patient_name}</td>
                    <td>
                        <a href="/static/pdf_reports/${row.file_name}" target="_blank">
                            View PDF
                        </a>
                    </td>
                    <td>${row.whatsapp_number}</td>
                    <td>${row.created_at}</td>
                `;
                tbody.appendChild(tr);
            });

        } catch (err) {
            console.error(err);
        }
    };

    /* ===============================
       ADD REPORT
    =============================== */
   form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const submitBtn = document.getElementById("submit_btn");
    submitBtn.disabled = true;
    submitBtn.innerText = "Processing...";

    const formData = new FormData(form);

    try {
        const res = await fetch("/add_report", {
            method: "POST",
            body: formData
        });

        const result = await res.json();

        if (result.status === "success") {
            form.reset();
            fetchTodayReports();
        } else {
            alert(result.message || "Failed");
        }

    } catch (err) {
        alert("Server error");
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerText = "Add Report";
    }
});


    // Auto load table
    fetchTodayReports();
});
