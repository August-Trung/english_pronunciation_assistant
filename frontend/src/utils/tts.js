/**
 * Shared Text-to-Speech (TTS) utility prioritizing British English (en-GB).
 * Rule: Priority & Default is ALWAYS British English (en-GB).
 */

export const getBritishVoice = () => {
  if (typeof window === 'undefined' || !('speechSynthesis' in window)) return null
  const voices = window.speechSynthesis.getVoices()
  // Priority 1: Exact en-GB language
  let voice = voices.find(v => v.lang === 'en-GB' || v.lang === 'en_GB')
  // Priority 2: Contains 'United Kingdom', 'UK', or 'British' in name
  if (!voice) {
    voice = voices.find(v => /united kingdom|uk|british/i.test(v.name) && v.lang.startsWith('en'))
  }
  // Priority 3: Any English voice
  if (!voice) {
    voice = voices.find(v => v.lang.startsWith('en'))
  }
  return voice || null
}

export const speakBritishText = (text, rate = 0.9, onEnd = null) => {
  if (typeof window === 'undefined' || !('speechSynthesis' in window) || !text) return null
  window.speechSynthesis.cancel()
  const utterance = new SpeechSynthesisUtterance(text)
  utterance.lang = 'en-GB'
  utterance.rate = rate
  const voice = getBritishVoice()
  if (voice) {
    utterance.voice = voice
  }
  if (onEnd) {
    utterance.onend = onEnd
    utterance.onerror = onEnd
  }
  window.speechSynthesis.speak(utterance)
  return utterance
}

export const speakTextWithAccent = (text, accent = 'en-GB', gender = 'female', rate = 0.85) => {
  if (typeof window === 'undefined' || !('speechSynthesis' in window) || !text) return null
  window.speechSynthesis.cancel()
  const utterance = new SpeechSynthesisUtterance(text)
  utterance.lang = accent || 'en-GB'
  utterance.rate = rate
  
  const voices = window.speechSynthesis.getVoices()
  let matching = voices.filter(v => v.lang.toLowerCase().replace('_', '-').includes(accent.toLowerCase().replace('_', '-')))
  if (!matching.length) {
    matching = voices.filter(v => v.lang.startsWith('en'))
  }
  if (gender && matching.length) {
    const genderVoice = matching.find(v => gender === 'female' 
      ? /female|zira|susan|hazel|serena|victoria/i.test(v.name) 
      : /male|david|mark|george|oliver/i.test(v.name))
    if (genderVoice) utterance.voice = genderVoice
    else if (matching[0]) utterance.voice = matching[0]
  } else if (matching[0]) {
    utterance.voice = matching[0]
  }
  
  window.speechSynthesis.speak(utterance)
  return utterance
}
