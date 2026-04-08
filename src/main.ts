import "./assets/main.css";
import { createApp } from "vue";
import App from "./App.vue";
import { Amplify } from "aws-amplify";
import outputs from "../amplify_outputs.json";
import router from './router/router'
Amplify.configure(outputs);

import {library} from '@fortawesome/fontawesome-svg-core';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { faMagnifyingGlass, faCircleUser } from "@fortawesome/free-solid-svg-icons";

library.add(faMagnifyingGlass,faCircleUser);

createApp(App).use(router).component("font-awesome-icon", FontAwesomeIcon).mount("#app");