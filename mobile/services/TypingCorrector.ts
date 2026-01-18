/**
 * Typing Corrector Service
 *
 * Uses ONNX Runtime to run the quantized typing correction model.
 * The model is a fine-tuned Qwen2.5-0.5B that corrects typos.
 */

import { InferenceSession, Tensor } from 'onnxruntime-react-native';
import { File } from 'expo-file-system';

// Tokenizer vocabulary (loaded from tokenizer.json)
let vocab: Map<string, number> | null = null;
let reverseVocab: Map<number, string> | null = null;
let merges: [string, string][] | null = null;

// ONNX session
let session: InferenceSession | null = null;

// Special tokens
const SPECIAL_TOKENS = {
  BOS: 151643, // <|endoftext|>
  EOS: 151643,
  IM_START: 151644, // <|im_start|>
  IM_END: 151645, // <|im_end|>
};

/**
 * Simple BPE tokenizer for Qwen-style models
 */
class SimpleTokenizer {
  private vocab: Map<string, number>;
  private reverseVocab: Map<number, string>;

  constructor(vocabData: Record<string, number>) {
    this.vocab = new Map(Object.entries(vocabData));
    this.reverseVocab = new Map();
    for (const [token, id] of this.vocab) {
      this.reverseVocab.set(id, token);
    }
  }

  /**
   * Simple encoding - uses byte-level BPE fallback
   */
  encode(text: string): number[] {
    const tokens: number[] = [];

    // Encode as UTF-8 bytes with Ġ prefix for space handling
    const bytes = new TextEncoder().encode(text);

    for (let i = 0; i < bytes.length; i++) {
      const byte = bytes[i];
      // Standard byte tokens in Qwen vocab
      const byteToken = String.fromCharCode(byte);
      const tokenId = this.vocab.get(byteToken);

      if (tokenId !== undefined) {
        tokens.push(tokenId);
      } else {
        // Fallback: use byte fallback tokens (common in BPE tokenizers)
        // Format varies by tokenizer, this is simplified
        const hexToken = `<0x${byte.toString(16).toUpperCase().padStart(2, '0')}>`;
        const hexId = this.vocab.get(hexToken);
        if (hexId !== undefined) {
          tokens.push(hexId);
        }
        // If still not found, skip (shouldn't happen with proper vocab)
      }
    }

    return tokens;
  }

  /**
   * Decode token IDs back to text
   */
  decode(tokenIds: number[]): string {
    const tokens: string[] = [];

    for (const id of tokenIds) {
      // Skip special tokens
      if (id >= 151643) continue;

      const token = this.reverseVocab.get(id);
      if (token) {
        // Handle Ġ (space prefix in GPT-style tokenizers)
        const decoded = token.replace(/Ġ/g, ' ');
        tokens.push(decoded);
      }
    }

    return tokens.join('');
  }
}

let tokenizer: SimpleTokenizer | null = null;

/**
 * Initialize the typing corrector model and tokenizer
 */
export async function initializeModel(
  modelPath: string,
  vocabPath: string
): Promise<void> {
  console.log('Loading vocabulary...');

  // Load vocab using new File API
  const vocabFile = new File(vocabPath);
  const vocabContent = await vocabFile.text();
  const vocabData = JSON.parse(vocabContent);
  tokenizer = new SimpleTokenizer(vocabData);

  console.log('Loading ONNX model...');

  // Load ONNX model
  session = await InferenceSession.create(modelPath);

  console.log('Model loaded successfully!');
  console.log('Input names:', session.inputNames);
  console.log('Output names:', session.outputNames);
}

/**
 * Build the prompt for the model
 */
function buildPrompt(text: string): string {
  return `<|im_start|>user
Correct this text: ${text}<|im_end|>
<|im_start|>assistant
`;
}

/**
 * Correct typos in the given text
 */
export async function correctTypos(text: string): Promise<string> {
  if (!session || !tokenizer) {
    throw new Error('Model not initialized. Call initializeModel first.');
  }

  // Build prompt
  const prompt = buildPrompt(text);

  // Tokenize
  const inputIds = tokenizer.encode(prompt);

  // Create input tensors
  const inputTensor = new Tensor('int64', BigInt64Array.from(inputIds.map(BigInt)), [
    1,
    inputIds.length,
  ]);

  const attentionMask = new Tensor(
    'int64',
    BigInt64Array.from(inputIds.map(() => BigInt(1))),
    [1, inputIds.length]
  );

  // Run inference
  const feeds: Record<string, Tensor> = {
    input_ids: inputTensor,
    attention_mask: attentionMask,
  };

  // For causal LM, we need to generate tokens autoregressively
  let generatedIds = [...inputIds];
  const maxNewTokens = 100;

  for (let i = 0; i < maxNewTokens; i++) {
    const currentInputTensor = new Tensor(
      'int64',
      BigInt64Array.from(generatedIds.map(BigInt)),
      [1, generatedIds.length]
    );

    const currentAttentionMask = new Tensor(
      'int64',
      BigInt64Array.from(generatedIds.map(() => BigInt(1))),
      [1, generatedIds.length]
    );

    const output = await session.run({
      input_ids: currentInputTensor,
      attention_mask: currentAttentionMask,
    });

    // Get logits from output
    const logits = output.logits || output.output;
    if (!logits) {
      throw new Error('No logits output from model');
    }

    // Get the last token's logits
    const logitsData = logits.data as Float32Array;
    const vocabSize = logitsData.length / generatedIds.length;
    const lastTokenLogits = logitsData.slice(-vocabSize);

    // Argmax to get the next token
    let maxIdx = 0;
    let maxVal = lastTokenLogits[0];
    for (let j = 1; j < lastTokenLogits.length; j++) {
      if (lastTokenLogits[j] > maxVal) {
        maxVal = lastTokenLogits[j];
        maxIdx = j;
      }
    }

    // Check for EOS token or im_end
    if (maxIdx === SPECIAL_TOKENS.EOS || maxIdx === SPECIAL_TOKENS.IM_END) {
      break;
    }

    generatedIds.push(maxIdx);
  }

  // Decode only the new tokens (skip the prompt)
  const newTokens = generatedIds.slice(inputIds.length);
  const decoded = tokenizer.decode(newTokens);

  // Clean up the response (remove any trailing special tokens)
  return decoded.replace(/<\|.*?\|>/g, '').trim();
}

/**
 * Check if the model is loaded
 */
export function isModelLoaded(): boolean {
  return session !== null && tokenizer !== null;
}

/**
 * Unload the model to free memory
 */
export async function unloadModel(): Promise<void> {
  if (session) {
    // session.release() if available
    session = null;
  }
  tokenizer = null;
}
