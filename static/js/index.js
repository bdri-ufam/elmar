const selectedUser = document.querySelector("#userId");

selectedUser?.addEventListener("change", (event) => {
  //console.log("Usuário selecionado: ", event.target.value);
  getUsersFunds(event.target.value);
});

function getData(endpoint, callback, params) {
  const request = new XMLHttpRequest();
  request.onreadystatechange = () => {
    if (request.readyState === XMLHttpRequest.DONE && request.status === 200) {
      //console.log("A requisição deu certo");
      callback(request.response);
    }
  };
  //  if (params == "") {
  //    request.open(method, endpoint, true);
  //  } else {
  request.open("GET", endpoint + "?" + params, true);
  //  }
  request.send();
}

function getUsersFunds(userId) {
  getData("/funds/", updateFundsTable, `userid=${userId}`);
}

function updateFundsTable(funds) {
  funds = JSON.parse(funds);

  const table = document.getElementById("userTable");

  table.innerHTML = `<thead>
        <tr>
          <th scope="col">#</th>
          <th scope="col">Available Funds</th>
          <th scope="col">Applied by the Client</th>
        </tr>
      </thead>`;

  const tbody = document.createElement("tbody");

  for (let i = 0; i < funds?.candidate_set?.length; i++) {
    const row = document.createElement("tr");

    let userFund = "";
    if (i < funds.user_funds.length) {
      userFund = `<td>${funds.user_funds[i]}</td>`;
    }

    row.innerHTML = `
    <th scope="row">${i + 1}</th>
    <td>${funds.candidate_set[i]}</td>
    ${userFund}
    `;
    tbody.appendChild(row);
  }
  table.appendChild(tbody);
}

$(document).ready(function () {
  $(".toast").toast("show");
});

const toast_stack_container_elem = document.getElementById(
  "toast-stack-container"
);

function showToast(category, message) {
  $("#frontToast")?.remove();

  const new_toast = document.createElement("div");
  new_toast.id = "frontToast";
  new_toast.classList.add("toast", "mt-0");
  new_toast.setAttribute("role", "alert");
  new_toast.setAttribute("aria-atomic", "true");
  new_toast.setAttribute("data-bs-autohide", "true");

  let headerMessage;
  switch (category) {
    case "error":
      headerMessage = "Please, verify!";
      new_toast.classList.add("border-danger");
      new_toast.setAttribute("aria-live", "assertive");
      new_toast.setAttribute("data-stack-toast-category", "error");
      break;
    case "info":
      headerMessage = "Information!";
      new_toast.classList.add("border-primary");
      new_toast.setAttribute("aria-live", "assertive");
      break;
    case "success":
      headerMessage = "Success!";
      new_toast.classList.add("border-success");
      new_toast.setAttribute("aria-live", "polite");
      break;
  }
  new_toast.classList.add("fade");

  new_toast.innerHTML += `<div class="toast-header">
      <strong class="me-auto text-black">${headerMessage}</strong>
      <small>Just Now</small>
      <button
        type="button"
        class="btn-close"
        data-bs-dismiss="toast"
        aria-label="Close"
      ></button>
    </div>
    <div class="toast-body toast-message">${message}</div>
  `;

  toast_stack_container_elem.append(new_toast);

  let myToast = bootstrap.Toast.getOrCreateInstance($("#frontToast")[0]);

  myToast.show();
}

$("#recsys_form").submit(function (event) {
  event.preventDefault();

  const userId = document.getElementById("userId").value;

  if (isNaN(Number(userId))) {
    showToast("error", "Select a valid SAKS User!");
    return false;
  }

  const numRec = document.getElementById("numRec").value;

  if (isNaN(Number(numRec))) {
    showToast("error", "Select the #number of recommendation!");
    return false;
  }

  showToast(
    "info",
    "PLEASE WAIT... The complete response may take about 2 or 3 minutes..."
  );

  $(".btn").attr("disabled", true);

  getData(
    "/preferences/",
    updatePreferences,
    `userid=${userId}&numRec=${numRec}`
  );

  return true;
});

function updatePreferences(completion) {
  completion = JSON.parse(completion);

  if (completion == null || completion == undefined) {
    showToast(
      "error",
      "We can not generate the answer now. Please, try again later."
    );
    $(".btn").attr("disabled", false);
    return;
  }

  if (jQuery.isEmptyObject(completion)) {
    showToast(
      "error",
      "We can not generate the answer now. Please, try again later."
    );
    $(".btn").attr("disabled", false);
    return;
  }

  document.getElementById("prefsOutput").innerHTML = completion.preferences;

  showToast(
    "info",
    "User preferences available. Wait for the recommendations."
  );

  $.ajax({
    type: "POST",
    url: "/recommendation/",
    data: JSON.stringify({ prefsCompletion: completion.completion }),
    contentType: "application/json",
    success: function (recsysCompletion) {
      //recsysCompletion = JSON.parse(data);
      //recsysCompletion = data;

      if (recsysCompletion == null || recsysCompletion == undefined) {
        showToast(
          "error",
          "We can not generate the recommendation now. Please, try again later."
        );
        $(".btn").attr("disabled", false);
        return;
      }

      if (jQuery.isEmptyObject(recsysCompletion)) {
        showToast(
          "error",
          "We can not generate the recommendation now. Please, try again later."
        );
        $(".btn").attr("disabled", false);
        return;
      }

      document.getElementById("recsysOutput").innerHTML =
        recsysCompletion.recommendation;

      $(".btn").attr("disabled", false);
    },
    error: function () {
      showToast(
        "error",
        "We can not generate the recommendation now. Please, try again later."
      );
      $(".btn").attr("disabled", false);
    },
  });
}
