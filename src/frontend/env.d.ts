/// <reference types="vite/client" />

interface ImportMetaEnv {
    VITE_SERVICES_BASEURL: string;
}

interface ImportMeta {
    readonly env: ImportMetaEnv;
}