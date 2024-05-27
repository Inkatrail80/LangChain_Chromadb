css = '''
<style>
h2 {
    font-family: Arial;
    font-size:30px;
}
input{
    background-color: #f1c411 !important;
    box-shadow: 3px 3px 3px black;
}
.chat-message {
    padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem; display: flex
}
.chat-message.user {
    background-color: #2d8aa3;
    box-shadow: 3px 3px 3px black;
}
.chat-message.bot {
    background-color: #475063;
    box-shadow: 3px 3px 3px black;
}
.chat-message.source {
    background-color: yellow;
    box-shadow: 3px 3px 3px black;
}
.chat-message .avatar {
  max-width:content;
}
.chat-message .avatar img {
  max-width: 78px;
  max-height: 78px;
  border-radius: 50%;
  object-fit: cover;
}

.message-text-user::before,
.message-text-user::after {
  content: "";
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
}

.message-text-user::before {
    background-color: #2d8aa3;
    animation: typewriter 4s
    steps(40) forwards;
} 

.message-text-user::after {
  width: 1.5px;
  background: black;
  animation: typewriter 4s
      steps(40) forwards,
    blink 500ms steps(40) infinite;
}

.message-text-bot::before,
.message-text-bot::after {
  content: "";
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
}

.message-text-bot::before {
    background-color: #475063;
    animation: typewriter 4s
    steps(40) forwards;
} 

.message-text-bot::after {
  width: 1.5px;
  background: black;
  animation: typewriter 4s
      steps(40) forwards,
    blink 500ms steps(40) infinite;
}

@keyframes typewriter {
  to {
    left: 100%;
  }
}

@keyframes blink {
  0% {
    background: black;
  }
  25% {
    background: transparent;
  }
  75% {
    background: transparent;
  }
  100% {
    background: black;
  }
}

.chat-message .message {
  padding: 0 1.5rem;
  color:whitesmoke;
  word-wrap: break-word;
  opacity: 0;
  overflow: hidden;
  animation: fadeIn 2s forwards;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
'''

bot_template = '''
<div class="chat-message bot">
    <div class="avatar">
        <img src="https://www.isportconnect.com/wp-content/uploads/2023/04/happy-robot-1024x683.jpg" style="max-height: 78px; max-width: 78px; border-radius: 50%; object-fit: cover;">
    </div>
    <div class="bot-message message">
    <p class="message-text-bot">{{MSG}}</p>
    </div>
</div>
'''

source_template = '''
<div class="chat-message source">
    <div class="avatar">
        <img src="https://i.ibb.co/cN0nmSj/Screenshot-2023-05-28-at-02-37-21.png" style="max-height: 78px; max-width: 78px; border-radius: 50%; object-fit: cover;">
    </div>
    <div class="bot-message message">
    <p class="message-text-source">{{MSG}}</p>
    </div>
</div>
'''

user_template = '''
<div class="chat-message user">
    <div class="avatar">
        <img src="https://cdn12.picryl.com/photo/2016/12/31/ball-question-mark-man-people-446773-1024.jpg">
    </div>    
    <div class="user-message message">
    <p class="message-text-user">{{MSG}}</p></div>
</div>
'''
