"""
test_file_mri.py - Testa la validazione dei file MRI NIfTI.

Verifica che solo file con i magic bytes NIfTI/gzip corretti vengano
accettati, e che file falsi, vuoti o con estensione sbagliata vengano
rifiutati prima di essere scritti su disco.
OWASP: API3 - Broken Object Property Level Authorization.
"""

import pytest
from fastapi import HTTPException


# Magic bytes costruiti a runtime (evita sequenze hex nel sorgente Python).
GZIP_MAGIC = bytes([0x1f, 0x8b])          # gzip signature
NI1_MAGIC  = bytes([110, 105, 49, 0])      # "ni1" + null, NIfTI-1 offset 344
NP1_MAGIC  = bytes([110,  43, 49, 0])      # "n+1" + null, NIfTI-1 offset 344
NI2_MAGIC  = bytes([110, 105, 50, 0])      # "ni2" + null, NIfTI-2 offset 4
NP2_MAGIC  = bytes([110,  43, 50, 0])      # "n+2" + null, NIfTI-2 offset 4


def valida_file_mri(filename: str, content: bytes) -> bytes:
    """Replica sincrona di _validate_mri_file (orchestrator/routers/analyze.py)."""
    if not filename.endswith((".nii", ".nii.gz")):
        raise HTTPException(status_code=400, detail="Formato non supportato")
    if len(content) < 1024:
        raise HTTPException(status_code=422, detail="File troppo piccolo o vuoto")
    is_gzip   = content[:2] == GZIP_MAGIC
    is_nifti1 = len(content) > 348 and content[344:348] in (NI1_MAGIC, NP1_MAGIC)
    is_nifti2 = len(content) > 8   and content[4:8]     in (NI2_MAGIC, NP2_MAGIC)
    if not (is_gzip or is_nifti1 or is_nifti2):
        raise HTTPException(status_code=422, detail="Il file non e un NIfTI valido")
    return content


@pytest.fixture
def file_nifti_gzip_valido(tmp_path):
    """File .nii.gz con magic bytes gzip corretti (1024 byte minimi)."""
    content = GZIP_MAGIC + bytes(1022)
    f = tmp_path / "scan_test.nii.gz"
    f.write_bytes(content)
    return f


@pytest.fixture
def file_nifti1_valido(tmp_path):
    """File .nii NIfTI-1 con magic NP1 offset 344."""
    content = bytearray(2048)
    content[344:348] = NP1_MAGIC
    f = tmp_path / "scan_nifti1.nii"
    f.write_bytes(bytes(content))
    return f


@pytest.fixture
def file_nifti2_valido(tmp_path):
    """File .nii NIfTI-2 con magic NP2 offset 4."""
    content = bytearray(2048)
    content[4:8] = NP2_MAGIC
    f = tmp_path / "scan_nifti2.nii"
    f.write_bytes(bytes(content))
    return f


@pytest.fixture
def file_vuoto(tmp_path):
    """File completamente vuoto (0 byte)."""
    f = tmp_path / "vuoto.nii.gz"
    f.write_bytes(b"")
    return f


@pytest.fixture
def file_piccolo(tmp_path):
    """File di soli 100 byte - sotto la soglia minima di 1024."""
    f = tmp_path / "piccolo.nii.gz"
    f.write_bytes(GZIP_MAGIC + bytes(98))
    return f


@pytest.fixture
def file_falso(tmp_path):
    """File .nii.gz con testo normale (nessun magic byte NIfTI)."""
    content = b"Questo file non e NIfTI. Nessun magic byte." * 30
    f = tmp_path / "falso.nii.gz"
    f.write_bytes(content)
    return f


@pytest.fixture
def file_binario_generico(tmp_path):
    """Eseguibile Windows (PE magic MZ) rinominato come .nii.gz."""
    content = bytes([0x4d, 0x5a]) + bytes(1022)  # MZ = PE header Windows
    f = tmp_path / "eseguibile.nii.gz"
    f.write_bytes(content)
    return f


def test_file_nifti_gzip_valido_accettato(file_nifti_gzip_valido):
    """Un file .nii.gz con magic bytes gzip deve essere accettato."""
    content = file_nifti_gzip_valido.read_bytes()
    result = valida_file_mri(file_nifti_gzip_valido.name, content)
    assert result == content


def test_file_nifti1_valido_accettato(file_nifti1_valido):
    """Un file .nii NIfTI-1 deve essere accettato."""
    content = file_nifti1_valido.read_bytes()
    result = valida_file_mri(file_nifti1_valido.name, content)
    assert result == content


def test_file_nifti2_valido_accettato(file_nifti2_valido):
    """Un file .nii NIfTI-2 deve essere accettato."""
    content = file_nifti2_valido.read_bytes()
    result = valida_file_mri(file_nifti2_valido.name, content)
    assert result == content


def test_file_vuoto_rifiutato(file_vuoto):
    """Un file vuoto deve essere rifiutato con HTTP 422."""
    content = file_vuoto.read_bytes()
    with pytest.raises(HTTPException) as exc_info:
        valida_file_mri(file_vuoto.name, content)
    assert exc_info.value.status_code == 422


def test_file_piccolo_rifiutato(file_piccolo):
    """Un file sotto i 1024 byte deve essere rifiutato con 422."""
    content = file_piccolo.read_bytes()
    with pytest.raises(HTTPException) as exc_info:
        valida_file_mri(file_piccolo.name, content)
    assert exc_info.value.status_code == 422


def test_file_falso_rifiutato(file_falso):
    """File con testo normale rinominato .nii.gz deve essere rifiutato con 422."""
    content = file_falso.read_bytes()
    with pytest.raises(HTTPException) as exc_info:
        valida_file_mri(file_falso.name, content)
    assert exc_info.value.status_code == 422


def test_file_binario_generico_rifiutato(file_binario_generico):
    """Eseguibile Windows rinominato come .nii.gz deve essere rifiutato."""
    content = file_binario_generico.read_bytes()
    with pytest.raises(HTTPException) as exc_info:
        valida_file_mri(file_binario_generico.name, content)
    assert exc_info.value.status_code == 422


@pytest.mark.parametrize("filename", [
    "scan.txt", "scan.jpg", "scan.pdf", "scan.exe", "scan.zip", "scan", "scan.bak",
])
def test_estensione_sbagliata_rifiutata(filename):
    """File con estensione non .nii/.nii.gz rifiutati con HTTP 400."""
    content = GZIP_MAGIC + bytes(1022)
    with pytest.raises(HTTPException) as exc_info:
        valida_file_mri(filename, content)
    assert exc_info.value.status_code == 400


def test_magic_ni1_accettato():
    content = bytearray(2048)
    content[344:348] = NI1_MAGIC
    assert valida_file_mri("scan.nii", bytes(content)) is not None


def test_magic_np1_accettato():
    content = bytearray(2048)
    content[344:348] = NP1_MAGIC
    assert valida_file_mri("scan.nii", bytes(content)) is not None


def test_magic_ni2_accettato():
    content = bytearray(2048)
    content[4:8] = NI2_MAGIC
    assert valida_file_mri("scan.nii", bytes(content)) is not None


def test_magic_np2_accettato():
    content = bytearray(2048)
    content[4:8] = NP2_MAGIC
    assert valida_file_mri("scan.nii", bytes(content)) is not None


def test_file_esattamente_1024_byte_accettato():
    """Esattamente 1024 byte (il minimo) deve essere accettato."""
    content = GZIP_MAGIC + bytes(1022)
    assert len(content) == 1024
    result = valida_file_mri("scan.nii.gz", content)
    assert len(result) == 1024


def test_file_1023_byte_rifiutato():
    """1023 byte (un byte sotto il minimo) deve essere rifiutato."""
    content = GZIP_MAGIC + bytes(1021)
    assert len(content) == 1023
    with pytest.raises(HTTPException) as exc_info:
        valida_file_mri("scan.nii.gz", content)
    assert exc_info.value.status_code == 422
