import { HardhatUserConfig } from 'hardhat/config';
import '@nomicfoundation/hardhat-toolbox';
import './tasks/deploy';
import dotenv from 'dotenv';
dotenv.config();

const rpcUrl = process.env.RPC_URL ?? '';
const etherscanApiKey = process.env.ETHERSCAN_API_KEY;

const deployer = process.env.DEPLOYER_PRIVATE_KEY;
const accounts = deployer ? [deployer] : [];

const config: HardhatUserConfig = {
  solidity: {
    version: '0.8.9',
    settings: {
      optimizer: {
        enabled: true,
        runs: 200,
      },
    },
  },
  networks: {
    goerli: { url: rpcUrl, accounts },
    mainnet: { url: rpcUrl, accounts },
  },
  etherscan: {
    apiKey: etherscanApiKey,
  },
};

export default config;
