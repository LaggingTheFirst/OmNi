const Encryption = {
    // Configuration
    algo: "AES-GCM",
    kdf: "PBKDF2",
    hash: "SHA-256",
    iterations: 100000,
    keyLen: 256,
    saltLen: 16,
    ivLen: 12,

    /**
     * Generate a random salt
     * @returns {Uint8Array}
     */
    generateSalt: function () {
        return window.crypto.getRandomValues(new Uint8Array(this.saltLen));
    },

    /**
     * Generate a random IV
     * @returns {Uint8Array}
     */
    generateIV: function () {
        return window.crypto.getRandomValues(new Uint8Array(this.ivLen));
    },

    /**
     * Derive a key from password and salt
     * @param {string} password 
     * @param {Uint8Array} salt 
     * @returns {Promise<CryptoKey>}
     */
    deriveKey: async function (password, salt) {
        const enc = new TextEncoder();
        const keyMaterial = await window.crypto.subtle.importKey(
            "raw",
            enc.encode(password),
            { name: this.kdf },
            false,
            ["deriveBits", "deriveKey"]
        );

        return window.crypto.subtle.deriveKey(
            {
                name: this.kdf,
                salt: salt,
                iterations: this.iterations,
                hash: this.hash
            },
            keyMaterial,
            { name: this.algo, length: this.keyLen },
            false, // Key not extractable
            ["encrypt", "decrypt"]
        );
    },

    /**
     * Encrypt a file
     * @param {Blob|File} file - The file to encrypt
     * @param {string} password - The encryption password
     * @returns {Promise<{blob: Blob, data: string}>} - Returns encrypted blob and JSON string with salt/iv
     */
    encryptFile: async function (file, password) {
        try {
            const salt = this.generateSalt();
            const iv = this.generateIV();
            const key = await this.deriveKey(password, salt);
            const fileBuffer = await file.arrayBuffer();

            const encryptedContent = await window.crypto.subtle.encrypt(
                {
                    name: this.algo,
                    iv: iv
                },
                key,
                fileBuffer
            );

            // Convert salt and iv to hex/base64 strings for storage
            const saltHex = this.buf2hex(salt);
            const ivHex = this.buf2hex(iv);

            // Create a blob from the encrypted data
            const encryptedBlob = new Blob([encryptedContent], { type: 'application/octet-stream' });

            return {
                blob: encryptedBlob,
                data: JSON.stringify({ salt: saltHex, iv: ivHex })
            };
        } catch (e) {
            console.error("Encryption error:", e);
            throw e;
        }
    },

    /**
     * Decrypt a file
     * @param {Blob} encryptedBlob - The encrypted file blob
     * @param {string} password - The decryption password
     * @param {string} encryptionDataJson - JSON string containing salt and iv
     * @returns {Promise<Blob>} - Returns decrypted file blob
     */
    decryptFile: async function (encryptedBlob, password, encryptionDataJson) {
        try {
            const data = JSON.parse(encryptionDataJson);
            const salt = this.hex2buf(data.salt);
            const iv = this.hex2buf(data.iv);

            const key = await this.deriveKey(password, salt);
            const encryptedBuffer = await encryptedBlob.arrayBuffer();

            const decryptedContent = await window.crypto.subtle.decrypt(
                {
                    name: this.algo,
                    iv: iv
                },
                key,
                encryptedBuffer
            );

            return new Blob([decryptedContent]);
        } catch (e) {
            console.error("Decryption error:", e);
            throw new Error("Incorrect password or corrupted file.");
        }
    },

    // Helpers
    /**
     * Convert buffer to hex string
     * @param {ArrayBuffer|Uint8Array} buffer 
     * @returns {string}
     */
    buf2hex: function (buffer) {
        return [...new Uint8Array(buffer)]
            .map(x => x.toString(16).padStart(2, '0'))
            .join('');
    },

    /**
     * Convert hex string to Uint8Array
     * @param {string} hexString 
     * @returns {Uint8Array}
     */
    hex2buf: function (hexString) {
        return new Uint8Array(hexString.match(/.{1,2}/g).map(byte => parseInt(byte, 16)));
    }
};
