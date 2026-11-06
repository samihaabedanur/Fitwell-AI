let classify, RawImage, prompts;
self.onmessage = async ({data}) => {
  try {
    if (data.prompts) {
      prompts = data.prompts;
      const transformers = await import('https://cdn.jsdelivr.net/npm/@huggingface/transformers@3.7.2/dist/transformers.min.js')
        .catch(() => import('https://unpkg.com/@huggingface/transformers@3.7.2/dist/transformers.min.js'));
      const {env, pipeline} = transformers;
      RawImage = transformers.RawImage;
      env.allowLocalModels = false;
      env.backends.onnx.wasm.numThreads = 1;
      env.backends.onnx.wasm.proxy = false;
      classify = await pipeline('zero-shot-image-classification', 'Xenova/clip-vit-base-patch32', {device:'wasm', dtype:'q8'});
      self.postMessage({ready:true});
      return;
    }
    const result = await classify(new RawImage(data, 224, 224, 4).rgb(), prompts, {
      hypothesis_template:'This is a photo of {}.',
    });
    self.postMessage({result});
  } catch (error) {
    self.postMessage({error:error.message});
  }
};
