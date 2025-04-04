import { Address } from "viem";

const shortAccount = (account: Address | undefined) => {
  if (!account) return "";
  return account.slice(0, 6) + "..." + account.slice(-4);
};

export default shortAccount;
