class Chatbox {
  constructor() {
    this.args = {
      openButton: document.querySelector(".chatbox__button"),
      chatBox: document.querySelector(".chatbox__support"),
      sendButton: document.querySelector(".send__button"),
      messageInput: document.querySelector(".chatbox__input"),
    };

    this.state = false;
    this.messages = [];
  }
  display() {
    const { openButton, chatBox, sendButton } = this.args;

    if (!openButton) {
      console.error("Open button not found.");
      return;
    }

    if (!chatBox) {
      console.error("Chat box not found.");
      return;
    }

    if (!sendButton) {
      console.error("Send button not found.");
      return;
    }

    openButton.addEventListener("click", () => this.toggleState(chatBox));

    sendButton.addEventListener("click", () => this.onSendButton(chatBox));

    const node = chatBox.querySelector("input");
    if (node) {
      node.addEventListener("keyup", ({ key }) => {
        if (key === "Enter") {
          this.onSendButton(chatBox);
        }
      });
    }
  }

  toggleState(chatbox) {
    this.state = !this.state;

    if (this.state) {
      chatbox.classList.add("chatbox--active");
    } else {
      chatbox.classList.remove("chatbox--active");
    }
  }

  // onSendButton(chatbox) {
  //   var textField = chatbox.querySelector("input");

  //   if (!textField) {
  //     console.error("Input field not found.");
  //     return;
  //   }

  //   let text1 = textField.value;
  //   if (text1 === "") {
  //     return;
  //   }

  //   let msg1 = { name: "User", message: text1 };
  //   this.messages.push(msg1);

  //   fetch("http://127.0.0.1:5005/webhooks/rest/webhook", {
  //     method: "POST",
  //     body: JSON.stringify({
  //       sender: "user",
  //       message: text1,
  //     }),
  //     headers: {
  //       "Content-Type": "application/json",
  //     },
  //   })
  //     .then((response) => {
  //       if (!response.ok) {
  //         throw new Error(`HTTP error! Status: ${response.status}`);
  //       }
  //       return response.json();
  //     })
  //     .then((response) => {
  //       if (response && response.length > 0) {
  //         let rasaMessage = response[0].text;
  //         let msg2 = { name: "Pravin", message: rasaMessage };
  //         this.messages.push(msg2);
  //         this.updateChatText(chatbox);
  //         textField.value = "";
  //       } else {
  //         console.error("Empty or invalid response from Rasa.");
  //         this.updateChatText(chatbox);
  //         textField.value = "";
  //       }
  //     })
  //     .catch((error) => {
  //       console.error("Error:", error);
  //       this.updateChatText(chatbox);
  //       textField.value = "";
  //     });
  // }
  onSendButton(chatbox) {
    var textField = chatbox.querySelector("input");

    if (!textField) {
      console.error("Input field not found.");
      return;
    }

    let userMessage = { name: "User", message: textField.value };
    this.messages.push(userMessage);

    fetch("http://127.0.0.1:5005/webhooks/rest/webhook", {
      method: "POST",
      body: JSON.stringify({
        sender: "user",
        message: textField.value,
      }),
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
      })
      .then((response) => {
        if (response && response.length > 0) {
          let chatbotMessage = { name: " ", message: response[0].text };
          this.messages.push(chatbotMessage);
          this.updateChatText(chatbox);
          textField.value = "";
        } else {
          console.error("Empty or invalid response from Rasa.");
          this.updateChatText(chatbox);
          textField.value = "";
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        this.updateChatText(chatbox);
        textField.value = "";
      });
  }

  handleRasaResponse(response, chatbox, inputField) {
    if (Array.isArray(response) && response.length > 0 && response[0].text) {
      const rasaMessage = { name: " ", message: response[0].text };
      this.messages.push(rasaMessage);
    } else {
      console.error("Invalid or empty response from Rasa.");
    }

    this.updateChatText(chatbox);
    inputField.value = "";
  }

  handleError(error, chatbox, inputField) {
    console.error("Error:", error);
    this.updateChatText(chatbox);
    inputField.value = "";
  }


  updateChatText(chatbox) {
    var html = "";
    this.messages.slice().forEach(function (item, index) {
      if (item.name === " ") {
        html =
          '<div class="messages__item messages__item--operator">' +
          item.message +
          "</div>" +
          html;
      } else {
        html =
          '<div class="messages__item messages__item--visitor">' +
          item.message +
          "</div>" +
          html;
      }
    });

    const chatmessage = chatbox.querySelector(".chatbox__messages");
    chatmessage.innerHTML = html;
  }

  createMessageElement(item) {
    const className =
      item.name === " "
        ? "messages__item--operator"
        : "messages__item--visitor";
    return `<div class="messages__item ${className}">${item.message}</div>`;
  }
}

const chatbox = new Chatbox();
chatbox.display();
