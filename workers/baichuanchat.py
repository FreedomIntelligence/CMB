from .base import *


class BaichuanChatWorker(BaseWorker):
    def load_model_and_tokenizer(self, load_config):
        hf_model_config = {
            "pretrained_model_name_or_path": load_config["config_dir"],
            "trust_remote_code": True,
            "low_cpu_mem_usage": True,
        }
        hf_tokenizer_config = {
            "pretrained_model_name_or_path": load_config["config_dir"],
            "padding_side": "left",
            "trust_remote_code": True,
        }
        device = load_config.get("device", "cuda")
        assert device == "cuda", "only supports CUDA inference"

        precision = load_config.get("precision", "fp16")

        if precision == "fp16":
            hf_model_config.update({"torch_dtype": torch.float16})

        tokenizer = AutoTokenizer.from_pretrained(**hf_tokenizer_config)
        
        model = AutoModelForCausalLM.from_pretrained(**hf_model_config)
        model.eval()
        return model, tokenizer


    @property
    def system_prompt(self):
        return ""

    @property
    def instruction_template(
        self,
    ):
        return self.system_prompt + "<reserved_102>{instruction}<reserved_103>"

    @property
    def instruction_template_with_fewshot(
        self,
    ):
        return self.system_prompt + "{fewshot_examples}<reserved_102>{instruction}<reserved_103>"

    @property
    def fewshot_template(self, eos="</s>"):
        return "<reserved_102>{user}<reserved_103>{gpt}" + eos

    def collate_conv(self, data, eos="</s>"):
        returned = []  # this is fed into the model for outputs
        partial_qas = []
        line = self.system_prompt

        id = data["id"]
        title = data["title"]
        description = data["description"]
        convs = data["QA_pairs"]

        for i, conv in enumerate(convs):
            if i == 0:
                line += "<reserved_102>{}{} ".format(
                    description, conv["question"]
                )  # a space after the patients' input
            else:
                line += "<reserved_102>{} ".format(
                    conv["question"]
                )  # a space after the patients' input
            returned.append(line + "<reserved_103>")

            partial_qas.append(
                {
                    "id": id,
                    "title": title,
                    "description": description,
                    "QA_pairs": deepcopy(convs[: i + 1]),  # a list
                }
            )

            line += "<reserved_103>{}".format(conv["solution"]) + eos
        return returned, partial_qas

   