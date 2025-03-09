declare global {
  namespace NodeJS {
    interface ProcessEnv {
      NEXT_PUBLIC_W3A_CLIENT_ID: string;
      W3A_CLIENT_SECRET: string;
    }
  }
}

export { }