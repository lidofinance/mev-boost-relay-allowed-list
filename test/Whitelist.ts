import { loadFixture } from '@nomicfoundation/hardhat-network-helpers';
import { SignerWithAddress } from '@nomiclabs/hardhat-ethers/signers';
import { MaxUint256 } from '@ethersproject/constants';
import { expect } from 'chai';
import { ethers } from 'hardhat';
import { MEVBoostAllowedRelaysList } from '../typechain-types';

interface Fixture {
  contract: MEVBoostAllowedRelaysList;
  accounts: SignerWithAddress[];
  relays: string[];
}

describe('MEV-Boost allowed relays list', () => {
  const deployContractFixture = async (): Promise<Fixture> => {
    const accounts = await ethers.getSigners();
    const relays = [
      'https://0xb124d80a00b80815397b4e7f1f05377ccc83aeeceb6be87963ba3649f1e6efa32ca870a88845917ec3f26a8e2aa25c77@one.mev-boost-relays.test',
      'https://0xafa4c6985aa049fb79dd37010438cfebeb0f2bd42b115b89dd678dab0670c1de38da0c4e9138c9290a398ecd9a0b3110@two.mev-boost-relays.test',
      'https://0xb5246e299aeb782fbc7c91b41b3284245b1ed5206134b0028b81dfb974e5900616c67847c2354479934fc4bb75519ee1@three.mev-boost-relays.test',
    ];

    const AllowedListFactory = await ethers.getContractFactory('MEVBoostAllowedRelaysList');
    const contract = await AllowedListFactory.deploy();

    return { contract, accounts, relays };
  };

  const addRelays = async (fixture: Pick<Fixture, 'contract' | 'relays'>) => {
    const { contract, relays } = fixture;

    for (const relay of relays) {
      await contract.addRelay(relay);
    }
  };

  const ERROR_CALLER_IS_NOT_OWNER = 'Ownable: caller is not the owner';
  const ERROR_URI_IS_EMPTY = 'Validation: uri is empty';
  const ERROR_OUT_OF_RANGE = 'Validation: index is out of range';

  describe('Deployment', () => {
    it('Should have the right owner', async () => {
      const { contract, accounts } = await loadFixture(deployContractFixture);
      const [owner] = accounts;

      expect(await contract.owner()).to.equal(owner.address);
    });

    it('Should have an empty relay list', async () => {
      const { contract } = await loadFixture(deployContractFixture);

      expect(await contract.getRelaysLength()).to.equal(0);
      expect(await contract.getRelays()).to.deep.equal([]);
    });
  });

  describe('Getters', () => {
    it('Should return an array of relays', async () => {
      const { contract, relays } = await loadFixture(deployContractFixture);
      await addRelays({ contract, relays });

      expect(await contract.getRelays())
        .to.deep.equal(relays)
        .and.have.length.greaterThan(1);
    });

    it('Should return the length of array', async () => {
      const { contract, relays } = await loadFixture(deployContractFixture);
      await addRelays({ contract, relays });

      expect(await contract.getRelaysLength())
        .to.equal(relays.length)
        .and.greaterThan(1);
    });
  });

  describe('Adding relays', () => {
    describe('Method call', () => {
      it('Should accept a call from the owner account', async () => {
        const { contract, accounts, relays } = await loadFixture(deployContractFixture);
        const [owner] = accounts;
        const [relay] = relays;

        await expect(contract.connect(owner).addRelay(relay)).not.to.be.reverted;
      });

      it('Should not accept a call from the unknown account', async () => {
        const { contract, accounts, relays } = await loadFixture(deployContractFixture);
        const [, unknown] = accounts;
        const [relay] = relays;

        await expect(contract.connect(unknown).addRelay(relay)).to.be.revertedWith(ERROR_CALLER_IS_NOT_OWNER);
      });

      it('Should add a relay', async () => {
        const { contract, accounts, relays } = await loadFixture(deployContractFixture);
        const [owner] = accounts;
        const [relay] = relays;

        expect(await contract.getRelays()).to.deep.equal([]);
        await contract.addRelay(relay);
        expect(await contract.getRelays()).to.deep.equal([relay]);
      });

      it('Should not add empty relay URI', async () => {
        const { contract } = await loadFixture(deployContractFixture);

        await expect(contract.addRelay('')).to.be.revertedWith(ERROR_URI_IS_EMPTY);
      });
    });

    describe('Events', () => {
      it('Should emit an event on adding', async () => {
        const { contract, relays } = await loadFixture(deployContractFixture);
        const [relay] = relays;

        await expect(contract.addRelay(relay)).to.emit(contract, 'RelayAdded').withArgs(relay);
      });
    });
  });

  describe('Removing relays', () => {
    describe('Method call', () => {
      it('Should accept a call from the owner account', async () => {
        const { contract, accounts, relays } = await loadFixture(deployContractFixture);
        const [owner] = accounts;

        await addRelays({ contract, relays });
        await expect(contract.connect(owner).removeRelay(0)).not.to.be.reverted;
      });

      it('Should not accept a call from the unknown account', async () => {
        const { contract, accounts, relays } = await loadFixture(deployContractFixture);
        const [, unknown] = accounts;

        await addRelays({ contract, relays });
        await expect(contract.connect(unknown).removeRelay(0)).to.be.revertedWith(ERROR_CALLER_IS_NOT_OWNER);
      });

      it('Should remove a relay', async () => {
        const { contract, relays } = await loadFixture(deployContractFixture);
        const [deletedRelay, ...restRelays] = relays;

        await addRelays({ contract, relays });
        await contract.removeRelay(0);

        expect(await contract.getRelays())
          .to.have.length(restRelays.length)
          .and.have.members(restRelays)
          .and.not.include(deletedRelay);
      });

      it('Should revert if array is empty', async () => {
        const { contract } = await loadFixture(deployContractFixture);

        await expect(contract.removeRelay(0)).to.be.revertedWith(ERROR_OUT_OF_RANGE);
      });

      it('Should revert if index is out of range', async () => {
        const { contract, relays } = await loadFixture(deployContractFixture);
        const totalRelays = relays.length;

        await addRelays({ contract, relays });
        await expect(contract.removeRelay(totalRelays)).to.be.revertedWith(ERROR_OUT_OF_RANGE);
        await expect(contract.removeRelay(totalRelays + 1)).to.be.revertedWith(ERROR_OUT_OF_RANGE);
        await expect(contract.removeRelay(MaxUint256)).to.be.revertedWith(ERROR_OUT_OF_RANGE);
      });

      it('Should move the last element in place of the deleted', async () => {
        const { contract, relays } = await loadFixture(deployContractFixture);

        await addRelays({ contract, relays });
        await contract.removeRelay(0);
        const [firstRelayInContract] = await contract.getRelays();
        const lastInitialRelay = relays[relays.length - 1];

        expect(firstRelayInContract).to.equal(lastInitialRelay);
      });
    });

    describe('Events', () => {
      it('Should emit an event on removing', async () => {
        const { contract, relays } = await loadFixture(deployContractFixture);
        const [deletedRelay] = relays;

        await addRelays({ contract, relays });
        await expect(contract.removeRelay(0)).to.emit(contract, 'RelayRemoved').withArgs(deletedRelay, 0);
      });
    });
  });
});
