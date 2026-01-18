import React, { useState, useEffect, useCallback } from 'react';
import { StatusBar } from 'expo-status-bar';
import {
  StyleSheet,
  Text,
  View,
  TextInput,
  TouchableOpacity,
  ActivityIndicator,
  SafeAreaView,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
} from 'react-native';
import { Paths, Directory, File } from 'expo-file-system';
import {
  initializeModel,
  correctTypos,
  isModelLoaded,
} from './services/TypingCorrector';

// Model download URL (for production, host on your CDN)
const MODEL_URL =
  'https://your-cdn.com/models/model_quantized.onnx';
const VOCAB_URL =
  'https://your-cdn.com/models/vocab.json';

export default function App() {
  const [inputText, setInputText] = useState('');
  const [correctedText, setCorrectedText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isModelReady, setIsModelReady] = useState(false);
  const [modelStatus, setModelStatus] = useState('Initializing...');
  const [error, setError] = useState<string | null>(null);

  // Initialize model on app start
  useEffect(() => {
    loadModel();
  }, []);

  const loadModel = async () => {
    try {
      setModelStatus('Checking for model files...');

      // Use the new expo-file-system API
      const modelsDir = new Directory(Paths.document, 'models');
      const modelFile = new File(modelsDir, 'model_quantized.onnx');
      const vocabFile = new File(modelsDir, 'vocab.json');

      // Create models directory if it doesn't exist
      if (!modelsDir.exists) {
        modelsDir.create();
      }

      // Check if model exists locally
      if (!modelFile.exists || !vocabFile.exists) {
        setModelStatus(
          'Model not found locally.\n\nTo use this app:\n1. Download model_quantized.onnx (473MB)\n2. Download vocab.json\n3. Place them in the app\'s documents folder'
        );
        setError('Model files not found. See instructions above.');
        return;
      }

      setModelStatus('Loading model into memory...');
      await initializeModel(modelFile.uri, vocabFile.uri);

      setIsModelReady(true);
      setModelStatus('Model ready!');
      setError(null);
    } catch (err) {
      console.error('Failed to load model:', err);
      setError(`Failed to load model: ${err}`);
      setModelStatus('Failed to load model');
    }
  };

  const handleCorrect = async () => {
    if (!inputText.trim() || !isModelReady) return;

    setIsLoading(true);
    setError(null);

    try {
      const result = await correctTypos(inputText);
      setCorrectedText(result);
    } catch (err) {
      console.error('Correction failed:', err);
      setError(`Correction failed: ${err}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopy = () => {
    // In a real app, use Clipboard API
    console.log('Copied:', correctedText);
  };

  const handleClear = () => {
    setInputText('');
    setCorrectedText('');
    setError(null);
  };

  // Demo mode with mock corrections (for testing UI without model)
  const handleDemoCorrect = () => {
    // Simulated corrections for common typos
    const mockCorrections: Record<string, string> = {
      'helo': 'hello',
      'wrold': 'world',
      'teh': 'the',
      'taht': 'that',
      'i woudl liek': 'I would like',
      'thnak you': 'thank you',
      'waht time': 'what time',
    };

    let result = inputText;
    for (const [typo, correction] of Object.entries(mockCorrections)) {
      result = result.replace(new RegExp(typo, 'gi'), correction);
    }

    // Capitalize first letter
    if (result.length > 0) {
      result = result.charAt(0).toUpperCase() + result.slice(1);
    }

    setCorrectedText(result);
  };

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardView}
      >
        <ScrollView contentContainerStyle={styles.scrollContent}>
          {/* Header */}
          <View style={styles.header}>
            <Text style={styles.title}>Typing Corrector</Text>
            <Text style={styles.subtitle}>AI-powered typo correction</Text>
          </View>

          {/* Model Status */}
          <View style={styles.statusContainer}>
            <View
              style={[
                styles.statusIndicator,
                isModelReady ? styles.statusReady : styles.statusLoading,
              ]}
            />
            <Text style={styles.statusText}>{modelStatus}</Text>
          </View>

          {/* Input Section */}
          <View style={styles.section}>
            <Text style={styles.sectionLabel}>Input (with typos)</Text>
            <TextInput
              style={styles.textInput}
              multiline
              placeholder="Type or paste text with typos here..."
              placeholderTextColor="#999"
              value={inputText}
              onChangeText={setInputText}
              textAlignVertical="top"
            />
          </View>

          {/* Action Buttons */}
          <View style={styles.buttonRow}>
            <TouchableOpacity
              style={[
                styles.button,
                styles.primaryButton,
                (!isModelReady || isLoading) && styles.buttonDisabled,
              ]}
              onPress={handleCorrect}
              disabled={!isModelReady || isLoading || !inputText.trim()}
            >
              {isLoading ? (
                <ActivityIndicator color="#fff" size="small" />
              ) : (
                <Text style={styles.buttonText}>Correct</Text>
              )}
            </TouchableOpacity>

            <TouchableOpacity
              style={[styles.button, styles.secondaryButton]}
              onPress={handleDemoCorrect}
              disabled={!inputText.trim()}
            >
              <Text style={[styles.buttonText, styles.secondaryButtonText]}>
                Demo
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[styles.button, styles.outlineButton]}
              onPress={handleClear}
            >
              <Text style={[styles.buttonText, styles.outlineButtonText]}>
                Clear
              </Text>
            </TouchableOpacity>
          </View>

          {/* Error Display */}
          {error && (
            <View style={styles.errorContainer}>
              <Text style={styles.errorText}>{error}</Text>
            </View>
          )}

          {/* Output Section */}
          <View style={styles.section}>
            <Text style={styles.sectionLabel}>Corrected Output</Text>
            <View style={styles.outputContainer}>
              <Text style={styles.outputText}>
                {correctedText || 'Corrected text will appear here...'}
              </Text>
            </View>
          </View>

          {/* Info Footer */}
          <View style={styles.footer}>
            <Text style={styles.footerText}>
              Model: Qwen2.5-0.5B (LoRA fine-tuned)
            </Text>
            <Text style={styles.footerText}>
              Inference: ONNX Runtime (quantized INT8)
            </Text>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
      <StatusBar style="auto" />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  keyboardView: {
    flex: 1,
  },
  scrollContent: {
    padding: 20,
  },
  header: {
    alignItems: 'center',
    marginBottom: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
  },
  subtitle: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  statusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    padding: 12,
    borderRadius: 8,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  statusIndicator: {
    width: 10,
    height: 10,
    borderRadius: 5,
    marginRight: 10,
  },
  statusReady: {
    backgroundColor: '#4CAF50',
  },
  statusLoading: {
    backgroundColor: '#FF9800',
  },
  statusText: {
    fontSize: 14,
    color: '#666',
    flex: 1,
  },
  section: {
    marginBottom: 16,
  },
  sectionLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  textInput: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    minHeight: 120,
    borderWidth: 1,
    borderColor: '#ddd',
  },
  buttonRow: {
    flexDirection: 'row',
    gap: 10,
    marginBottom: 16,
  },
  button: {
    flex: 1,
    paddingVertical: 14,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
  },
  primaryButton: {
    backgroundColor: '#007AFF',
  },
  secondaryButton: {
    backgroundColor: '#E3F2FD',
  },
  outlineButton: {
    backgroundColor: 'transparent',
    borderWidth: 1,
    borderColor: '#ddd',
  },
  buttonDisabled: {
    opacity: 0.5,
  },
  buttonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#fff',
  },
  secondaryButtonText: {
    color: '#007AFF',
  },
  outlineButtonText: {
    color: '#666',
  },
  errorContainer: {
    backgroundColor: '#FFEBEE',
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
  },
  errorText: {
    color: '#C62828',
    fontSize: 14,
  },
  outputContainer: {
    backgroundColor: '#E8F5E9',
    borderRadius: 8,
    padding: 12,
    minHeight: 100,
  },
  outputText: {
    fontSize: 16,
    color: '#333',
    lineHeight: 24,
  },
  footer: {
    marginTop: 20,
    alignItems: 'center',
  },
  footerText: {
    fontSize: 12,
    color: '#999',
  },
});
