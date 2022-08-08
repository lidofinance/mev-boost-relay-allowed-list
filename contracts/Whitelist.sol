// SPDX-FileCopyrightText: 2022 Lido <info@lido.fi>
// SPDX-License-Identifier: GPL-3.0

pragma solidity ^0.8.0;

import '@openzeppelin/contracts/access/Ownable.sol';

/**
 * @notice Storage of the whitelisted MEB-Boost relays
 */
contract MEVBoostRelayWhitelist is Ownable {
    string[] internal _relays;

    event RelayAdded(string uri);
    event RelayRemoved(string uri, uint256 index);

    /**
     * @notice Returns an unordered array of whitelisted relay URIs
     * @return The relay URIs array
     */
    function getRelays() public view returns (string[] memory) {
        return _relays;
    }

    /**
     * @notice Returns the length of the array of whitelisted relay URIs
     * @return Length of the relay URIs array
     */
    function getRelaysLength() public view returns (uint256) {
        return _relays.length;
    }

    /**
     * @notice Adds relay URI to the whitelist
     * @param _uri Relay URI with pubkey (e.g. https://0xafa4c6985aa049fb79dd37010438cfebeb0f2bd42b115b89dd678dab0670c1de38da0c4e9138c9290a398ecd9a0b3110@builder-relay-goerli.flashbots.net)
     */
    function addRelay(string memory _uri) external onlyOwner {
        _addRelay(_uri);
    }

    function _addRelay(string memory _uri) internal {
        require(bytes(_uri).length > 0, 'Validation: uri is empty');

        _relays.push(_uri);
        emit RelayAdded(_uri);
    }

    /**
     * @notice Removes relay URI from the whitelist
     * @param _index Relay URI index to be deleted in the array
     */
    function removeRelay(uint256 _index) external onlyOwner {
        _removeRelay(_index);
    }

    function _removeRelay(uint256 _index) internal {
        uint256 relayLength = _relays.length;
        require(_index < relayLength, 'Validation: index is out of range');

        emit RelayRemoved(_relays[_index], _index);

        /// @dev Move the last element of the array to the place of the deleted one
        uint256 lastIndex = relayLength - 1;
        if (_index != lastIndex) {
            _relays[_index] = _relays[lastIndex];
        }

        _relays.pop();
    }
}
