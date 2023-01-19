"use strict";
exports.id = 103;
exports.ids = [103];
exports.modules = {

/***/ 70103:
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* binding */ fetchAdapter)
/* harmony export */ });
/* harmony import */ var axios__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(82585);
/* harmony import */ var axios__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(axios__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var axios_lib_core_settle__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(43614);
/* harmony import */ var axios_lib_core_settle__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(axios_lib_core_settle__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var axios_lib_helpers_buildURL__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(96324);
/* harmony import */ var axios_lib_helpers_buildURL__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(axios_lib_helpers_buildURL__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var axios_lib_core_buildFullPath__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(38303);
/* harmony import */ var axios_lib_core_buildFullPath__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(axios_lib_core_buildFullPath__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var axios_lib_utils__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(27027);
/* harmony import */ var axios_lib_utils__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(axios_lib_utils__WEBPACK_IMPORTED_MODULE_4__);






/**
 * - Create a request object
 * - Get response body
 * - Check if timeout
 */
async function fetchAdapter(config) {
    const request = createRequest(config);
    const promiseChain = [getResponse(request, config)];

    if (config.timeout && config.timeout > 0) {
        promiseChain.push(
            new Promise((res) => {
                setTimeout(() => {
                    const message = config.timeoutErrorMessage
                        ? config.timeoutErrorMessage
                        : 'timeout of ' + config.timeout + 'ms exceeded';
                    res(createError(message, config, 'ECONNABORTED', request));
                }, config.timeout);
            })
        );
    }

    const data = await Promise.race(promiseChain);
    return new Promise((resolve, reject) => {
        if (data instanceof Error) {
            reject(data);
        } else {
            Object.prototype.toString.call(config.settle) === '[object Function]'
                ? config.settle(resolve, reject, data)
                : axios_lib_core_settle__WEBPACK_IMPORTED_MODULE_1___default()(resolve, reject, data);
        }
    });
}


/**
 * Fetch API stage two is to get response body. This funtion tries to retrieve
 * response body based on response's type
 */
async function getResponse(request, config) {
    let stageOne;
    try {
        stageOne = await fetch(request);
        
        const response = {
          ok: stageOne.ok,
          status: stageOne.status,
          statusText: stageOne.statusText,
          headers: new Headers(stageOne.headers), // Make a copy of headers
          config: config,
          request,
        }

        if (stageOne.status >= 400) {
          return createError('Response Error', config, 'ERR_NETWORK', request, response);
        }
    } catch (e) {
        return createError('Network Error', config, 'ERR_NETWORK', request);
    }

    const response = {
        ok: stageOne.ok,
        status: stageOne.status,
        statusText: stageOne.statusText,
        headers: new Headers(stageOne.headers), // Make a copy of headers
        config: config,
        request,
    };

    if (stageOne.status >= 200 && stageOne.status !== 204) {
        switch (config.responseType) {
            case 'arraybuffer':
                response.data = await stageOne.arrayBuffer();
                break;
            case 'blob':
                response.data = await stageOne.blob();
                break;
            case 'json':
                response.data = await stageOne.json();
                break;
            case 'formData':
                response.data = await stageOne.formData();
                break;
            default:
                response.data = await stageOne.text();
                break;
        }
    }

    return response;
}

/**
 * This function will create a Request object based on configuration's axios
 */
function createRequest(config) {
    const headers = new Headers(config.headers);

    // HTTP basic authentication
    if (config.auth) {
        const username = config.auth.username || '';
        const password = config.auth.password ? decodeURI(encodeURIComponent(config.auth.password)) : '';
        headers.set('Authorization', `Basic ${btoa(username + ':' + password)}`);
    }

    const method = config.method.toUpperCase();
    const options = {
        headers: headers,
        method,
    };
    if (method !== 'GET' && method !== 'HEAD') {
        options.body = config.data;

        // In these cases the browser will automatically set the correct Content-Type,
        // but only if that header hasn't been set yet. So that's why we're deleting it.
        if ((0,axios_lib_utils__WEBPACK_IMPORTED_MODULE_4__.isFormData)(options.body) && (0,axios_lib_utils__WEBPACK_IMPORTED_MODULE_4__.isStandardBrowserEnv)()) {
            headers.delete('Content-Type');
        }
    }
    if (config.mode) {
        options.mode = config.mode;
    }
    if (config.cache) {
        options.cache = config.cache;
    }
    if (config.integrity) {
        options.integrity = config.integrity;
    }
    if (config.redirect) {
        options.redirect = config.redirect;
    }
    if (config.referrer) {
        options.referrer = config.referrer;
    }
    // This config is similar to XHR’s withCredentials flag, but with three available values instead of two.
    // So if withCredentials is not set, default value 'same-origin' will be used
    if (!(0,axios_lib_utils__WEBPACK_IMPORTED_MODULE_4__.isUndefined)(config.withCredentials)) {
        options.credentials = config.withCredentials ? 'include' : 'omit';
    }

    const fullPath = axios_lib_core_buildFullPath__WEBPACK_IMPORTED_MODULE_3___default()(config.baseURL, config.url);
    const url = axios_lib_helpers_buildURL__WEBPACK_IMPORTED_MODULE_2___default()(fullPath, config.params, config.paramsSerializer);

    // Expected browser to throw error if there is any wrong configuration value
    return new Request(url, options);
}



/**
 * Note:
 * 
 *   From version >= 0.27.0, createError function is replaced by AxiosError class.
 *   So I copy the old createError function here for backward compatible.
 * 
 * 
 * 
 * Create an Error with the specified message, config, error code, request and response.
 *
 * @param {string} message The error message.
 * @param {Object} config The config.
 * @param {string} [code] The error code (for example, 'ECONNABORTED').
 * @param {Object} [request] The request.
 * @param {Object} [response] The response.
 * @returns {Error} The created error.
 */
function createError(message, config, code, request, response) {
    if ((axios__WEBPACK_IMPORTED_MODULE_0___default().AxiosError) && typeof (axios__WEBPACK_IMPORTED_MODULE_0___default().AxiosError) === 'function') {
        return new (axios__WEBPACK_IMPORTED_MODULE_0___default().AxiosError)(message, (axios__WEBPACK_IMPORTED_MODULE_0___default().AxiosError)[code], config, request, response);
    }

    var error = new Error(message);
    return enhanceError(error, config, code, request, response);
};

/**
 * 
 * Note:
 * 
 *   This function is for backward compatible.
 * 
 *  
 * Update an Error with the specified config, error code, and response.
 *
 * @param {Error} error The error to update.
 * @param {Object} config The config.
 * @param {string} [code] The error code (for example, 'ECONNABORTED').
 * @param {Object} [request] The request.
 * @param {Object} [response] The response.
 * @returns {Error} The error.
 */
function enhanceError(error, config, code, request, response) {
  error.config = config;
  if (code) {
    error.code = code;
  }

  error.request = request;
  error.response = response;
  error.isAxiosError = true;

  error.toJSON = function toJSON() {
    return {
      // Standard
      message: this.message,
      name: this.name,
      // Microsoft
      description: this.description,
      number: this.number,
      // Mozilla
      fileName: this.fileName,
      lineNumber: this.lineNumber,
      columnNumber: this.columnNumber,
      stack: this.stack,
      // Axios
      config: this.config,
      code: this.code,
      status: this.response && this.response.status ? this.response.status : null
    };
  };
  return error;
};


/***/ })

};
;