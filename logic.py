# logic.py
import wave
import zlib
import os
import tempfile
from security import encrypt_file, decrypt_file

def create_header(secret_filename, original_size, final_payload_size, flags):
    filename_bytes = secret_filename.encode('utf-8')
    header = flags.to_bytes(1, 'big')
    header += filename_bytes.ljust(255, b'\0')
    header += original_size.to_bytes(4, 'big')
    header += final_payload_size.to_bytes(4, 'big')
    return header

def parse_header(stego_frames):
    header_bytes_to_read = 264
    if len(stego_frames) < header_bytes_to_read * 8:
        raise ValueError("Stego file is too small.")
    header_bits = ''.join(str(frame & 1) for frame in stego_frames[:header_bytes_to_read * 8])
    header_bytes = bytearray(int(header_bits[i:i+8], 2) for i in range(0, len(header_bits), 8))
    
    flags = header_bytes[0]
    is_compressed = (flags & 1) == 1
    is_encrypted = (flags & 2) == 2
    filename = header_bytes[1:256].rstrip(b'\0').decode('utf-8')
    original_size = int.from_bytes(header_bytes[256:260], 'big')
    final_payload_size = int.from_bytes(header_bytes[260:264], 'big')
    return filename, original_size, final_payload_size, is_compressed, is_encrypted

def hide_data(cover_path, secret_data, secret_filename, output_path, password, compress, use_encryption, progress_callback):
    temp_in_path, temp_out_path = None, None
    try:
        progress_callback("Processing secret data...", 0.1)
        original_size = len(secret_data)
        flags = 0
        
        with tempfile.NamedTemporaryFile(delete=False) as temp_in_file:
            temp_in_path = temp_in_file.name
            if compress:
                progress_callback("Compressing data...", 0.2)
                secret_data = zlib.compress(secret_data, level=9)
                flags |= 1
            temp_in_file.write(secret_data)

        if use_encryption:
            progress_callback("Encrypting data (Auto-AES)...", 0.3)
            with tempfile.NamedTemporaryFile(delete=False) as temp_out_file:
                temp_out_path = temp_out_file.name
            # Use the provided internal password
            encrypt_file(temp_in_path, temp_out_path, password)
            file_to_hide_path = temp_out_path
            flags |= 2
        else:
            file_to_hide_path = temp_in_path

        with open(file_to_hide_path, 'rb') as f:
            final_payload_data = f.read()
        final_payload_size = len(final_payload_data)

        if os.path.exists(temp_in_path): os.remove(temp_in_path)
        if use_encryption and temp_out_path and os.path.exists(temp_out_path): 
            os.remove(temp_out_path)
            
        progress_callback("Creating header...", 0.4)
        header = create_header(secret_filename, original_size, final_payload_size, flags)
        data_to_hide = header + final_payload_data
        
        progress_callback("Reading cover audio...", 0.5)
        with wave.open(cover_path, 'rb') as cover_audio:
            params = cover_audio.getparams()
            cover_frames = bytearray(cover_audio.readframes(cover_audio.getnframes()))
        
        if len(data_to_hide) * 8 > len(cover_frames):
            raise ValueError("Cover audio is too small.")
            
        progress_callback("Hiding data...", 0.6)
        bits_to_hide = ''.join(format(byte, '08b') for byte in data_to_hide)
        
        for i, bit in enumerate(bits_to_hide):
            cover_frames[i] = (cover_frames[i] & 0b11111110) | int(bit)
            if i % 50000 == 0:
                progress_callback(f"Hiding... {int((i/len(bits_to_hide))*100)}%", 0.6 + 0.3 * (i / len(bits_to_hide)))

        progress_callback("Writing output file...", 0.9)
        with wave.open(output_path, 'wb') as stego_audio:
            stego_audio.setparams(params)
            stego_audio.writeframes(bytes(cover_frames))
        progress_callback("Done!", 1.0)

    except Exception as e:
        if temp_in_path and os.path.exists(temp_in_path): os.remove(temp_in_path)
        if temp_out_path and os.path.exists(temp_out_path): os.remove(temp_out_path)
        raise e

def extract_data(stego_path, password, progress_callback):
    temp_in_path, temp_out_path = None, None
    try:
        progress_callback("Reading stego audio...", 0.1)
        with wave.open(stego_path, 'rb') as stego_audio:
            stego_frames = bytearray(stego_audio.readframes(stego_audio.getnframes()))

        progress_callback("Parsing header...", 0.25)
        filename, original_size, final_payload_size, is_compressed, is_encrypted = parse_header(stego_frames)
        
        header_size_bytes = 264
        progress_callback("Extracting bits...", 0.4)
        
        bits_to_extract = final_payload_size * 8
        if (header_size_bytes * 8 + bits_to_extract) > len(stego_frames):
             raise ValueError("File corrupted.")

        start_idx = header_size_bytes * 8
        end_idx = start_idx + bits_to_extract
        extracted_bits = ''.join(str(stego_frames[i] & 1) for i in range(start_idx, end_idx))

        progress_callback("Reconstructing payload...", 0.7)
        extracted_payload = bytearray(int(extracted_bits[i:i+8], 2) for i in range(0, len(extracted_bits), 8))

        with tempfile.NamedTemporaryFile(delete=False) as temp_in_file:
            temp_in_path = temp_in_file.name
            temp_in_file.write(extracted_payload)

        if is_encrypted:
            progress_callback("Decrypting (Auto-AES)...", 0.8)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.dec') as temp_out_file:
                temp_out_path = temp_out_file.name
            
            decrypt_file(temp_in_path, temp_out_path, password)
            processed_file_path = temp_out_path
        else:
            processed_file_path = temp_in_path

        with open(processed_file_path, 'rb') as f:
            secret_data = f.read()

        if os.path.exists(temp_in_path): os.remove(temp_in_path)
        if is_encrypted and temp_out_path and os.path.exists(temp_out_path): os.remove(temp_out_path)

        if is_compressed:
            progress_callback("Decompressing...", 0.9)
            secret_data = zlib.decompress(secret_data)
        
        secret_data = secret_data[:original_size]
        progress_callback("Done!", 1.0)
        return secret_data, filename

    except Exception as e:
        if temp_in_path and os.path.exists(temp_in_path): os.remove(temp_in_path)
        if temp_out_path and os.path.exists(temp_out_path): os.remove(temp_out_path)
        raise e