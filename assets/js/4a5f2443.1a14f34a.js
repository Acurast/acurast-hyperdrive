"use strict";(self.webpackChunkdocumentation=self.webpackChunkdocumentation||[]).push([[934],{3905:(t,e,r)=>{r.d(e,{Zo:()=>c,kt:()=>f});var a=r(67294);function n(t,e,r){return e in t?Object.defineProperty(t,e,{value:r,enumerable:!0,configurable:!0,writable:!0}):t[e]=r,t}function o(t,e){var r=Object.keys(t);if(Object.getOwnPropertySymbols){var a=Object.getOwnPropertySymbols(t);e&&(a=a.filter((function(e){return Object.getOwnPropertyDescriptor(t,e).enumerable}))),r.push.apply(r,a)}return r}function i(t){for(var e=1;e<arguments.length;e++){var r=null!=arguments[e]?arguments[e]:{};e%2?o(Object(r),!0).forEach((function(e){n(t,e,r[e])})):Object.getOwnPropertyDescriptors?Object.defineProperties(t,Object.getOwnPropertyDescriptors(r)):o(Object(r)).forEach((function(e){Object.defineProperty(t,e,Object.getOwnPropertyDescriptor(r,e))}))}return t}function s(t,e){if(null==t)return{};var r,a,n=function(t,e){if(null==t)return{};var r,a,n={},o=Object.keys(t);for(a=0;a<o.length;a++)r=o[a],e.indexOf(r)>=0||(n[r]=t[r]);return n}(t,e);if(Object.getOwnPropertySymbols){var o=Object.getOwnPropertySymbols(t);for(a=0;a<o.length;a++)r=o[a],e.indexOf(r)>=0||Object.prototype.propertyIsEnumerable.call(t,r)&&(n[r]=t[r])}return n}var l=a.createContext({}),p=function(t){var e=a.useContext(l),r=e;return t&&(r="function"==typeof t?t(e):i(i({},e),t)),r},c=function(t){var e=p(t.components);return a.createElement(l.Provider,{value:e},t.children)},d="mdxType",u={inlineCode:"code",wrapper:function(t){var e=t.children;return a.createElement(a.Fragment,{},e)}},m=a.forwardRef((function(t,e){var r=t.components,n=t.mdxType,o=t.originalType,l=t.parentName,c=s(t,["components","mdxType","originalType","parentName"]),d=p(r),m=n,f=d["".concat(l,".").concat(m)]||d[m]||u[m]||o;return r?a.createElement(f,i(i({ref:e},c),{},{components:r})):a.createElement(f,i({ref:e},c))}));function f(t,e){var r=arguments,n=e&&e.mdxType;if("string"==typeof t||n){var o=r.length,i=new Array(o);i[0]=m;var s={};for(var l in e)hasOwnProperty.call(e,l)&&(s[l]=e[l]);s.originalType=t,s[d]="string"==typeof t?t:n,i[1]=s;for(var p=2;p<o;p++)i[p]=r[p];return a.createElement.apply(null,i)}return a.createElement.apply(null,r)}m.displayName="MDXCreateElement"},35949:(t,e,r)=>{r.r(e),r.d(e,{assets:()=>l,contentTitle:()=>i,default:()=>d,frontMatter:()=>o,metadata:()=>s,toc:()=>p});var a=r(87462),n=(r(67294),r(3905));const o={title:"EIP-1186 Proof Validator",slug:"/relay-contracts/tezos/validator",hide_title:!0},i=void 0,s={unversionedId:"relay-contracts/tezos/validator",id:"relay-contracts/tezos/validator",title:"EIP-1186 Proof Validator",description:"Implementations",source:"@site/docs/relay-contracts/tezos/validator.mdx",sourceDirName:"relay-contracts/tezos",slug:"/relay-contracts/tezos/validator",permalink:"/acurast-hyperdrive/relay-contracts/tezos/validator",draft:!1,editUrl:"https://github.com/Acurast/acurast-hyperdrive/tree/main/apps/documentation/docs/relay-contracts/tezos/validator.mdx",tags:[],version:"current",frontMatter:{title:"EIP-1186 Proof Validator",slug:"/relay-contracts/tezos/validator",hide_title:!0},sidebar:"docs",previous:{title:"State Aggregator",permalink:"/acurast-hyperdrive/relay-contracts/tezos/state"},next:{title:"Proof Validator",permalink:"/acurast-hyperdrive/relay-contracts/evm/validator"}},l={},p=[{value:"Implementations",id:"implementations",level:2},{value:"Methods",id:"methods",level:2},{value:"<code>submit_block_state_root</code>",id:"submit_block_state_root",level:3},{value:"<code>configure</code>",id:"configure",level:3},{value:"Views",id:"views",level:2},{value:"<code>validate_storage_proof</code>",id:"validate_storage_proof",level:3}],c={toc:p};function d(t){let{components:e,...r}=t;return(0,n.kt)("wrapper",(0,a.Z)({},c,r,{components:e,mdxType:"MDXLayout"}),(0,n.kt)("h2",{id:"implementations"},"Implementations"),(0,n.kt)("ul",null,(0,n.kt)("li",{parentName:"ul"},(0,n.kt)("a",{parentName:"li",href:"https://github.com/Acurast/acurast-hyperdrive/blob/main/contracts/tezos/IBCF_Eth_Validator.py"},"IBCF_Eth_Validator.py"))),(0,n.kt)("h2",{id:"methods"},"Methods"),(0,n.kt)("h3",{id:"submit_block_state_root"},(0,n.kt)("inlineCode",{parentName:"h3"},"submit_block_state_root")),(0,n.kt)("p",null,(0,n.kt)("strong",{parentName:"p"},"Input type:")),(0,n.kt)("pre",null,(0,n.kt)("code",{parentName:"pre"},"(pair %submit_block_state_root\n    (nat %block_number)\n    (bytes %state_root)\n)\n")),(0,n.kt)("p",null,(0,n.kt)("strong",{parentName:"p"},"Description:")," Validators call this method with the block state roots of an EVM ",(0,n.kt)("a",{parentName:"p",href:"https://eips.ethereum.org/EIPS/eip-1186"},"EIP-1186")," enabled chain."),(0,n.kt)("p",null,(0,n.kt)("strong",{parentName:"p"},"Requires permissions?")," Yes, only ",(0,n.kt)("inlineCode",{parentName:"p"},"validators")," can call this method."),(0,n.kt)("div",{class:"padding-vert--md"}),(0,n.kt)("h3",{id:"configure"},(0,n.kt)("inlineCode",{parentName:"h3"},"configure")),(0,n.kt)("p",null,(0,n.kt)("strong",{parentName:"p"},"Input type:")),(0,n.kt)("pre",null,(0,n.kt)("code",{parentName:"pre"},"(list %configure\n    (or\n        (address %update_administrator)\n        (nat %update_history_length)\n        (nat %update_minimum_endorsements)\n        (nat %update_snapshot_interval)\n        (set %update_validators (or (address %add) (address %remove)))\n    )\n)\n")),(0,n.kt)("p",null,(0,n.kt)("strong",{parentName:"p"},"Description:")," This method modifies the contract configurations."),(0,n.kt)("p",null,(0,n.kt)("strong",{parentName:"p"},"Requires permissions?")," Yes, only the multisig administrator can call this method."),(0,n.kt)("div",{class:"padding-vert--md"}),(0,n.kt)("h2",{id:"views"},"Views"),(0,n.kt)("h3",{id:"validate_storage_proof"},(0,n.kt)("inlineCode",{parentName:"h3"},"validate_storage_proof")),(0,n.kt)("p",null,(0,n.kt)("strong",{parentName:"p"},"Input type:")),(0,n.kt)("pre",null,(0,n.kt)("code",{parentName:"pre"},"(pair\n    (bytes %account)\n    (bytes %account_proof_rlp)\n    (nat %block_number)\n    (bytes %storage_proof_rlp)\n    (bytes %storage_slot)\n)\n")),(0,n.kt)("p",null,(0,n.kt)("strong",{parentName:"p"},"Output type:")," ",(0,n.kt)("inlineCode",{parentName:"p"},"bytes")),(0,n.kt)("p",null,(0,n.kt)("strong",{parentName:"p"},"Description:")," Contracts in a Tezos ecosystem can call this method to validate ",(0,n.kt)("a",{parentName:"p",href:"https://eips.ethereum.org/EIPS/eip-1186"},"EIP-1186")," storage slot proofs of EVM contracts."),(0,n.kt)("p",null,"If the proof is valid, it returns the ",(0,n.kt)("a",{parentName:"p",href:"https://ethereum.org/en/developers/docs/data-structures-and-encoding/rlp"},"RLP")," encoded value of the EVM contract storage slot."))}d.isMDXComponent=!0}}]);