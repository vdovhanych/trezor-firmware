from trezor.crypto import hashlib
from trezor.crypto.curve import ed25519
from trezor.messages import (
    CardanoAddressType,
    CardanoAuxiliaryDataType,
    CardanoMetadataType,
)

from apps.common import cbor

from .address import derive_address_bytes, derive_human_readable_address
from .helpers import INVALID_AUXILIARY_DATA, bech32
from .helpers.bech32 import HRP_JORMUN_PUBLIC_KEY
from .helpers.paths import SCHEMA_STAKING_ANY_ACCOUNT
from .helpers.utils import derive_public_key
from .layout import confirm_catalyst_registration, show_auxiliary_data_hash

if False:
    from typing import Union
    from trezor import wire

    from trezor.messages.CardanoCatalystRegistrationParametersType import (
        CardanoCatalystRegistrationParametersType,
    )
    from trezor.messages.CardanoTxAuxiliaryDataType import CardanoTxAuxiliaryDataType
    from trezor.messages.CardanoTxMetadataType import CardanoTxMetadataType

    CatalystRegistrationPayload = dict[int, Union[bytes, int]]
    CatalystRegistrationSignature = dict[int, bytes]
    CatalystRegistration = dict[
        int, Union[CatalystRegistrationPayload, CatalystRegistrationSignature]
    ]

    from . import seed

AUXILIARY_DATA_HASH_SIZE = 32
CATALYST_VOTING_PUBLIC_KEY_LENGTH = 32
CATALYST_REGISTRATION_HASH_SIZE = 32

METADATA_KEY_CATALYST_REGISTRATION = 61284
METADATA_KEY_CATALYST_REGISTRATION_SIGNATURE = 61285


def validate_auxiliary_data(
    keychain: seed.Keychain,
    auxiliary_data: CardanoTxAuxiliaryDataType | None,
    protocol_magic: int,
    network_id: int,
) -> None:
    if not auxiliary_data:
        return

    if auxiliary_data.type == CardanoAuxiliaryDataType.BLOB:
        if not auxiliary_data.blob:
            raise INVALID_AUXILIARY_DATA

        _validate_auxiliary_data_blob(auxiliary_data.blob)
    elif auxiliary_data.type == CardanoAuxiliaryDataType.TUPLE:
        if auxiliary_data.blob:
            raise INVALID_AUXILIARY_DATA

        # currently only metadata is supported as part of auxiliary data
        if auxiliary_data.metadata:
            _validate_metadata(
                keychain, auxiliary_data.metadata, protocol_magic, network_id
            )
        else:
            raise INVALID_AUXILIARY_DATA
    else:
        raise INVALID_AUXILIARY_DATA


def _validate_auxiliary_data_blob(auxiliary_data_blob: bytes) -> None:
    try:
        # this also raises an error if there's some data remaining
        cbor.decode(auxiliary_data_blob)
    except Exception:
        raise INVALID_AUXILIARY_DATA


def _validate_metadata(
    keychain: seed.Keychain,
    metadata: CardanoTxMetadataType,
    protocol_magic: int,
    network_id: int,
) -> None:
    if metadata.type == CardanoMetadataType.CATALYST_REGISTRATION:
        _validate_catalyst_registration_parameters(
            keychain,
            metadata.catalyst_registration_parameters,
            protocol_magic,
            network_id,
        )
    else:
        raise INVALID_AUXILIARY_DATA


def _validate_catalyst_registration_parameters(
    keychain: seed.Keychain,
    catalyst_registration_parameters: CardanoCatalystRegistrationParametersType | None,
    protocol_magic: int,
    network_id: int,
) -> None:
    if not catalyst_registration_parameters:
        raise INVALID_AUXILIARY_DATA

    if (
        len(catalyst_registration_parameters.voting_public_key)
        != CATALYST_VOTING_PUBLIC_KEY_LENGTH
    ):
        raise INVALID_AUXILIARY_DATA

    if not SCHEMA_STAKING_ANY_ACCOUNT.match(
        catalyst_registration_parameters.staking_path
    ):
        raise INVALID_AUXILIARY_DATA

    address_parameters = catalyst_registration_parameters.reward_address_parameters
    if address_parameters.address_type == CardanoAddressType.BYRON:
        raise INVALID_AUXILIARY_DATA

    # try to derive the address to validate it
    derive_address_bytes(keychain, address_parameters, protocol_magic, network_id)


async def show_auxiliary_data(
    ctx: wire.Context,
    keychain: seed.Keychain,
    auxiliary_data: CardanoTxAuxiliaryDataType | None,
    protocol_magic: int,
    network_id: int,
) -> None:
    if not auxiliary_data:
        return

    if auxiliary_data.metadata:
        await _show_metadata(
            ctx, keychain, auxiliary_data.metadata, protocol_magic, network_id
        )

    auxiliary_data_bytes = get_auxiliary_data_cbor(
        keychain, auxiliary_data, protocol_magic, network_id
    )
    # get_auxiliary_data_bytes returns none only if auxiliary_data is None, which is checked above
    assert auxiliary_data_bytes is not None

    auxiliary_data_hash = hash_auxiliary_data(bytes(auxiliary_data_bytes))
    await show_auxiliary_data_hash(ctx, auxiliary_data_hash)


async def _show_metadata(
    ctx: wire.Context,
    keychain: seed.Keychain,
    metadata: CardanoTxMetadataType,
    protocol_magic: int,
    network_id: int,
) -> None:
    if metadata.type == CardanoMetadataType.CATALYST_REGISTRATION:
        # ensured by _validate_metadata
        assert metadata.catalyst_registration_parameters is not None

        await _show_catalyst_registration(
            ctx,
            keychain,
            metadata.catalyst_registration_parameters,
            protocol_magic,
            network_id,
        )


async def _show_catalyst_registration(
    ctx: wire.Context,
    keychain: seed.Keychain,
    catalyst_registration_parameters: CardanoCatalystRegistrationParametersType,
    protocol_magic: int,
    network_id: int,
) -> None:
    public_key = catalyst_registration_parameters.voting_public_key
    encoded_public_key = bech32.encode(HRP_JORMUN_PUBLIC_KEY, public_key)
    staking_path = catalyst_registration_parameters.staking_path
    reward_address = derive_human_readable_address(
        keychain,
        catalyst_registration_parameters.reward_address_parameters,
        protocol_magic,
        network_id,
    )
    nonce = catalyst_registration_parameters.nonce

    await confirm_catalyst_registration(
        ctx, encoded_public_key, staking_path, reward_address, nonce
    )


def get_auxiliary_data_cbor(
    keychain: seed.Keychain,
    auxiliary_data: CardanoTxAuxiliaryDataType,
    protocol_magic: int,
    network_id: int,
) -> bytes:
    if auxiliary_data.type == CardanoAuxiliaryDataType.BLOB:
        # ensured by _validate_auxiliary_data
        assert auxiliary_data.blob is not None

        return auxiliary_data.blob
    elif auxiliary_data.type == CardanoAuxiliaryDataType.TUPLE:
        # currently only metadata is supported as part of auxiliary data
        if auxiliary_data.metadata:
            cborized_metadata = _cborize_metadata(
                keychain, auxiliary_data.metadata, protocol_magic, network_id
            )
            return cbor.encode(_wrap_metadata(cborized_metadata))
        else:
            raise INVALID_AUXILIARY_DATA
    else:
        raise INVALID_AUXILIARY_DATA


def _cborize_metadata(
    keychain: seed.Keychain,
    metadata: CardanoTxMetadataType,
    protocol_magic: int,
    network_id: int,
) -> CatalystRegistration:
    if metadata.type == CardanoMetadataType.CATALYST_REGISTRATION:
        # ensured by _validate_metadata
        assert metadata.catalyst_registration_parameters is not None

        return _cborize_catalyst_registration(
            keychain,
            metadata.catalyst_registration_parameters,
            protocol_magic,
            network_id,
        )


def _cborize_catalyst_registration(
    keychain: seed.Keychain,
    catalyst_registration_parameters: CardanoCatalystRegistrationParametersType,
    protocol_magic: int,
    network_id: int,
) -> CatalystRegistration:
    staking_key = derive_public_key(
        keychain, catalyst_registration_parameters.staking_path
    )

    catalyst_registration_payload: CatalystRegistrationPayload = {
        1: catalyst_registration_parameters.voting_public_key,
        2: staking_key,
        3: derive_address_bytes(
            keychain,
            catalyst_registration_parameters.reward_address_parameters,
            protocol_magic,
            network_id,
        ),
        4: catalyst_registration_parameters.nonce,
    }

    catalyst_registration_payload_signature = (
        _create_catalyst_registration_payload_signature(
            keychain,
            catalyst_registration_payload,
            catalyst_registration_parameters.staking_path,
        )
    )
    catalyst_registration_signature = {1: catalyst_registration_payload_signature}

    return {
        METADATA_KEY_CATALYST_REGISTRATION: catalyst_registration_payload,
        METADATA_KEY_CATALYST_REGISTRATION_SIGNATURE: catalyst_registration_signature,
    }


def _create_catalyst_registration_payload_signature(
    keychain: seed.Keychain,
    catalyst_registration_payload: CatalystRegistrationPayload,
    path: list[int],
) -> bytes:
    node = keychain.derive(path)

    encoded_catalyst_registration = cbor.encode(
        {METADATA_KEY_CATALYST_REGISTRATION: catalyst_registration_payload}
    )

    catalyst_registration_hash = hashlib.blake2b(
        data=encoded_catalyst_registration,
        outlen=CATALYST_REGISTRATION_HASH_SIZE,
    ).digest()

    return ed25519.sign_ext(
        node.private_key(), node.private_key_ext(), catalyst_registration_hash
    )


def _wrap_metadata(metadata: dict) -> tuple[dict, tuple]:
    """
    A new structure of metadata is used after Cardano Mary era. The metadata
    is wrapped in a tuple and auxiliary_scripts may follow it. Cardano
    tooling uses this new format of "wrapped" metadata even if no
    auxiliary_scripts are included. So we do the same here.

    https://github.com/input-output-hk/cardano-ledger-specs/blob/f7deb22be14d31b535f56edc3ca542c548244c67/shelley-ma/shelley-ma-test/cddl-files/shelley-ma.cddl#L212
    """
    return metadata, ()


def hash_auxiliary_data(auxiliary_data: bytes) -> bytes:
    return hashlib.blake2b(
        data=auxiliary_data, outlen=AUXILIARY_DATA_HASH_SIZE
    ).digest()
