import { task } from 'hardhat/config';

task('deploy', 'Deploy MEV-Boost relay whitelist contract').setAction(async (taskArgs, hre) => {
  const { ethers } = hre;

  const WhitelistFactory = await ethers.getContractFactory('MEVBoostRelayWhitelist');
  const contract = await WhitelistFactory.deploy();

  await contract.deployed();
  console.log('Contract deployed to:', contract.address);

  if (hre.network.name === 'localhost') return;

  console.log('Waiting a few blocks to be sure the data has been updated on Etherscan');
  await contract.deployTransaction.wait(5);

  await hre.run('verify:verify', { address: contract.address });
  console.log('Contract verified on etherscan');
});
