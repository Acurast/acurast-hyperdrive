"use strict";(self.webpackChunkdocumentation=self.webpackChunkdocumentation||[]).push([[261],{3905:(e,t,r)=>{r.d(t,{Zo:()=>p,kt:()=>h});var a=r(67294);function n(e,t,r){return t in e?Object.defineProperty(e,t,{value:r,enumerable:!0,configurable:!0,writable:!0}):e[t]=r,e}function o(e,t){var r=Object.keys(e);if(Object.getOwnPropertySymbols){var a=Object.getOwnPropertySymbols(e);t&&(a=a.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),r.push.apply(r,a)}return r}function s(e){for(var t=1;t<arguments.length;t++){var r=null!=arguments[t]?arguments[t]:{};t%2?o(Object(r),!0).forEach((function(t){n(e,t,r[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(r)):o(Object(r)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(r,t))}))}return e}function i(e,t){if(null==e)return{};var r,a,n=function(e,t){if(null==e)return{};var r,a,n={},o=Object.keys(e);for(a=0;a<o.length;a++)r=o[a],t.indexOf(r)>=0||(n[r]=e[r]);return n}(e,t);if(Object.getOwnPropertySymbols){var o=Object.getOwnPropertySymbols(e);for(a=0;a<o.length;a++)r=o[a],t.indexOf(r)>=0||Object.prototype.propertyIsEnumerable.call(e,r)&&(n[r]=e[r])}return n}var l=a.createContext({}),c=function(e){var t=a.useContext(l),r=t;return e&&(r="function"==typeof e?e(t):s(s({},t),e)),r},p=function(e){var t=c(e.components);return a.createElement(l.Provider,{value:t},e.children)},u="mdxType",d={inlineCode:"code",wrapper:function(e){var t=e.children;return a.createElement(a.Fragment,{},t)}},m=a.forwardRef((function(e,t){var r=e.components,n=e.mdxType,o=e.originalType,l=e.parentName,p=i(e,["components","mdxType","originalType","parentName"]),u=c(r),m=n,h=u["".concat(l,".").concat(m)]||u[m]||d[m]||o;return r?a.createElement(h,s(s({ref:t},p),{},{components:r})):a.createElement(h,s({ref:t},p))}));function h(e,t){var r=arguments,n=t&&t.mdxType;if("string"==typeof e||n){var o=r.length,s=new Array(o);s[0]=m;var i={};for(var l in t)hasOwnProperty.call(t,l)&&(i[l]=t[l]);i.originalType=e,i[u]="string"==typeof e?e:n,s[1]=i;for(var c=2;c<o;c++)s[c]=r[c];return a.createElement.apply(null,s)}return a.createElement.apply(null,r)}m.displayName="MDXCreateElement"},2768:(e,t,r)=>{r.r(t),r.d(t,{assets:()=>p,contentTitle:()=>l,default:()=>m,frontMatter:()=>i,metadata:()=>c,toc:()=>u});var a=r(87462),n=(r(67294),r(3905)),o=r(50941),s=r(44996);const i={title:"Overview",slug:"/trust-anchor",hide_title:!0},l=void 0,c={unversionedId:"relay-contracts/overview",id:"relay-contracts/overview",title:"Overview",description:"Tezos EVM",source:"@site/docs/relay-contracts/overview.mdx",sourceDirName:"relay-contracts",slug:"/trust-anchor",permalink:"/acurast-hyperdrive/trust-anchor",draft:!1,editUrl:"https://github.com/Acurast/acurast-hyperdrive/tree/main/apps/documentation/docs/relay-contracts/overview.mdx",tags:[],version:"current",frontMatter:{title:"Overview",slug:"/trust-anchor",hide_title:!0},sidebar:"docs",previous:{title:"Libraries",permalink:"/acurast-hyperdrive/toolkits"},next:{title:"State Aggregator",permalink:"/acurast-hyperdrive/relay-contracts/tezos/state"}},p={},u=[{value:"Tezos \u27a1\ufe0f EVM",id:"tezos-\ufe0f-evm",level:2},{value:"EVM \u27a1\ufe0f Tezos",id:"evm-\ufe0f-tezos",level:2}],d={toc:u};function m(e){let{components:t,...r}=e;return(0,n.kt)("wrapper",(0,a.Z)({},d,r,{components:t,mdxType:"MDXLayout"}),(0,n.kt)("h2",{id:"tezos-\ufe0f-evm"},"Tezos \u27a1\ufe0f EVM"),(0,n.kt)("p",null,"Sharing the state from Tezos to EVM involves interacting with two contracts (a ",(0,n.kt)("a",{parentName:"p",href:"/relay-contracts/tezos/state"},"State Aggregator")," and a ",(0,n.kt)("a",{parentName:"p",href:"/relay-contracts/evm/validator"},"Proof Validator"),")."),(0,n.kt)("center",null,(0,n.kt)(o.Z,{width:"480px",sources:{light:(0,s.Z)("/img/ibcf-relay-tezos-evm.svg"),dark:(0,s.Z)("/img/ibcf-relay-tezos-evm-dark.svg")},mdxType:"ThemedImage"})),(0,n.kt)("div",{class:"padding-vert--md"}),(0,n.kt)("p",null,"The \ud83d\udcd2 ",(0,n.kt)("a",{parentName:"p",href:"/relay-contracts/tezos/state"},(0,n.kt)("strong",{parentName:"a"},"State aggregation"))," contract acts as a database and proof generator for other contracts in the Tezos ecosystem.\nIt produces a snapshot of a Merkle tree every ",(0,n.kt)("inlineCode",{parentName:"p"},"X")," blocks, where the root node of the tree is used to validate all the proofs for the given snapshot."),(0,n.kt)("p",null,"The origin contract address is included on every added state to authenticate the proofs on the EVM chain."),(0,n.kt)("p",null,"The ",(0,n.kt)("strong",{parentName:"p"},"Merkle root")," of every snapshot is then transmitted to an EVM contract (\ud83d\udc6e\u200d\u2642\ufe0f ",(0,n.kt)("a",{parentName:"p",href:"/relay-contracts/evm/validator"},(0,n.kt)("strong",{parentName:"a"},"Proof Validator")),"), which allows the contracts on the EVM environment to validate the proofs of \u2709\ufe0f states added on Tezos at a given snapshot."),(0,n.kt)("p",null,"This step can be done from any Tezos chain to any EVM chain."),(0,n.kt)("ul",null,(0,n.kt)("li",{parentName:"ul"},"Tezos \u27a1\ufe0f Ethereum"),(0,n.kt)("li",{parentName:"ul"},"Tezos \u27a1\ufe0f Polygon"),(0,n.kt)("li",{parentName:"ul"},"Tezos \u27a1\ufe0f Binance Smart Chain"),(0,n.kt)("li",{parentName:"ul"},"Tezos \u27a1\ufe0f Avalanche"),(0,n.kt)("li",{parentName:"ul"},"Tezos \u27a1\ufe0f Moonbeam"),(0,n.kt)("li",{parentName:"ul"},"Tezos \u27a1\ufe0f Astar")),(0,n.kt)("h2",{id:"evm-\ufe0f-tezos"},"EVM \u27a1\ufe0f Tezos"),(0,n.kt)("p",null,"Sharing the state from an EVM chain to Tezos requires the EVM chain to be ",(0,n.kt)("a",{parentName:"p",href:"https://eips.ethereum.org/EIPS/eip-1186"},"EIP-1186")," enabled and a Tezos (\ud83d\udc6e\u200d\u2642\ufe0f ",(0,n.kt)("a",{parentName:"p",href:"/relay-contracts/tezos/validator"},(0,n.kt)("strong",{parentName:"a"},"Proof Validator")),") contract capable of validating ",(0,n.kt)("inlineCode",{parentName:"p"},"EIP-1186")," storage proofs."),(0,n.kt)("center",null,(0,n.kt)(o.Z,{width:"480px",sources:{light:(0,s.Z)("/img/ibcf-relay-evm-tezos.svg"),dark:(0,s.Z)("/img/ibcf-relay-evm-tezos-dark.svg")},mdxType:"ThemedImage"})),(0,n.kt)("div",{class:"padding-vert--md"}),(0,n.kt)("p",null,"The state transmitter first asks the Tezos (\ud83d\udc6e\u200d\u2642\ufe0f ",(0,n.kt)("a",{parentName:"p",href:"/relay-contracts/tezos/validator"},(0,n.kt)("strong",{parentName:"a"},"EIP-1186 Proof Validator")),") which ",(0,n.kt)("inlineCode",{parentName:"p"},"snapshot/block_level")," it is expecting, then queries the ",(0,n.kt)("strong",{parentName:"p"},"Merkle root")," of that ",(0,n.kt)("inlineCode",{parentName:"p"},"snapshot/block_level")," and sends it to the validator."),(0,n.kt)("p",null,"Applications can then leverage ",(0,n.kt)("a",{parentName:"p",href:"https://eips.ethereum.org/EIPS/eip-1186"},"EIP-1186")," for producing storage proofs of EVM contracts that get validated on Tezos."),(0,n.kt)("p",null,"Supported chains:"),(0,n.kt)("ul",null,(0,n.kt)("li",{parentName:"ul"},"Tezos \u27a1\ufe0f Ethereum"),(0,n.kt)("li",{parentName:"ul"},"Tezos \u27a1\ufe0f Polygon"),(0,n.kt)("li",{parentName:"ul"},"Tezos \u27a1\ufe0f Binance Smart Chain")))}m.isMDXComponent=!0}}]);