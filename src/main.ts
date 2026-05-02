import "./assets/main.css";
import { createApp } from "vue";
import App from "./App.vue";
import { Amplify } from "aws-amplify";
import outputs from "../amplify_outputs.json";
import router from './router/router'
Amplify.configure(outputs);

import {library} from '@fortawesome/fontawesome-svg-core';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { faMagnifyingGlass, faCircleUser ,faStar, faArrowsRotate} from "@fortawesome/free-solid-svg-icons";

library.add(faMagnifyingGlass,faCircleUser,faStar,faArrowsRotate);

createApp(App).use(router).component("font-awesome-icon", FontAwesomeIcon).mount("#app");
