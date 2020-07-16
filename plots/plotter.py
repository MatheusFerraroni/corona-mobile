import json
import numpy as np
import matplotlib.pyplot as plt

total_steps = 3914

arq_isolation = {}
arq_infeccao = {}
arq_tempo = {}


def read_logs(arquivos):
    
    for i in range(len(arquivos)):

        arq = arquivos[i]
        f = open("../log_output/{0}".format(arq),"r")
        infos = f.read().split("\n")
        f.close()

        infos.pop()
        for j in range(len(infos)):
            infos[j] = json.loads(infos[j])

        arquivos[i] = infos


    atual_veiculos = []
    atual_infectados = []
    total_infectados = []
    total_criado = []
    
    for i in range(total_steps):

        temp_atual_veiculos = []
        temp_atual_infectados = []
        temp_total_infectados = []
        temp_total_criado = []
        for j in range(len(arquivos)):
            try:
                temp_atual_veiculos.append(arquivos[j][i]["atual_veiculos"])
                temp_atual_infectados.append(arquivos[j][i]["atual_infectados"])
                temp_total_infectados.append(arquivos[j][i]["total_infectados"])
                temp_total_criado.append(arquivos[j][i]["total_criado"])
            except:
                temp_atual_veiculos.append(0)
                temp_atual_infectados.append(0)
                temp_total_infectados.append(0)
                temp_total_criado.append(0)

        atual_veiculos.append({"mean":np.mean(temp_atual_veiculos), "std": np.std(temp_atual_veiculos)})
        atual_infectados.append({"mean":np.mean(temp_atual_infectados), "std": np.std(temp_atual_infectados)})
        total_infectados.append({"mean":np.mean(temp_total_infectados), "std": np.std(temp_total_infectados)})
        total_criado.append({"mean":np.mean(temp_total_criado), "std": np.std(temp_total_criado)})

    return {"atual_veiculos":atual_veiculos, "atual_infectados":atual_infectados, "total_infectados":total_infectados, "total_criado":total_criado}





fig, axs = plt.subplots(2, 1, figsize=(12,8))
axs[0].set_title("Variando isolamento")
axs[0].set_ylim(-5, 3610)
axs[0].set_xlim(-1, 3610)
axs[1].set_ylim(-5, 200)
axs[1].set_xlim(-1, 3610)
axs[0].grid(True, ls="-.", lw=0.5)
axs[1].grid(True, ls="-.", lw=0.5)
axs[0].set_ylabel("Total Infectados")
axs[1].set_ylabel("Atual Infectados")
axs[1].set_xlabel("Timestep")

for i in np.arange(0.1, 1.0, 0.1):
    i = "{:.1f}".format(float(i))
    arq_isolation[i] = {}
    arq_isolation[i]["arquivos"] = []
    for cont in range(0,5,1):
        arq_isolation[i]["arquivos"].append(f'isolation_{i}_{cont}')
    arq_isolation[i]["dados"] = read_logs(arq_isolation[i]["arquivos"])



    ys = []
    errs = []
    xs = np.arange(total_steps)

    last_max = arq_isolation[i]["dados"]["total_infectados"][0]["mean"]
    for d in arq_isolation[i]["dados"]["total_infectados"]:
        last_max = max(last_max,d["mean"])
        ys.append(last_max)
        errs.append(d["std"])
    axs[0].errorbar(xs, ys, yerr=errs, errorevery=36, label='Isolamento {0}'.format(i))

    ys = []
    errs = []
    xs = np.arange(total_steps)
    for d in arq_isolation[i]["dados"]["atual_infectados"]:
        ys.append(d["mean"])
        errs.append(d["std"])
    axs[1].errorbar(xs, ys, yerr=errs, errorevery=36, label='Isolamento {0}'.format(i))

axs[0].legend(bbox_to_anchor=(0., 1.1, 1., .102), loc='lower left',
       ncol=3, mode="expand", borderaxespad=0.,shadow=True, fancybox=True)
plt.savefig("wuhan_isolation.pdf", bbox_inches="tight")








# fig, axs = plt.subplots(2, 1, figsize=(12,8))
# axs[0].set_title("Variando infecção")
# axs[0].set_ylim(-5, 3610)
# axs[0].set_xlim(-1, 3610)
# axs[1].set_ylim(-5, 200)
# axs[1].set_xlim(-1, 3610)
# axs[0].grid(True, ls="-.", lw=0.5)
# axs[1].grid(True, ls="-.", lw=0.5)
# axs[0].set_ylabel("Total Infectados")
# axs[1].set_ylabel("Atual Infectados")
# axs[1].set_xlabel("Timestep")


# for j in np.arange(0.1, 1.0, 0.1):
#     j = "{:.1f}".format(float(j))
#     arq_infeccao[j] = {}
#     arq_infeccao[j]["arquivos"] = []
#     for cont in range(10,20,1):
#         arq_infeccao[j]["arquivos"].append(f'infection_{j}_{cont}')
#     arq_infeccao[j]["dados"] = read_logs(arq_infeccao[j]["arquivos"])

#     ys = []
#     errs = []
#     xs = np.arange(total_steps)
#     for d in arq_infeccao[j]["dados"]["total_infectados"]:
#         ys.append(d["mean"])
#         errs.append(d["std"])
#     axs[0].errorbar(xs, ys, yerr=errs, errorevery=36, label='Infecção {0}'.format(j))

#     ys = []
#     errs = []
#     xs = np.arange(total_steps)
#     for d in arq_infeccao[j]["dados"]["atual_infectados"]:
#         ys.append(d["mean"])
#         errs.append(d["std"])
#     axs[1].errorbar(xs, ys, yerr=errs, errorevery=36, label='Infecção {0}'.format(j))

# axs[0].legend(bbox_to_anchor=(0., 1.1, 1., .102), loc='lower left',
#        ncol=3, mode="expand", borderaxespad=0.,shadow=True, fancybox=True)
# plt.savefig("grid_infection_high.pdf", bbox_inches="tight")





# fig, axs = plt.subplots(2, 1, figsize=(12,8))
# axs[0].set_title("Variando tempo infectado")
# axs[0].set_ylim(-5, 3610)
# axs[0].set_xlim(-1, 3610)
# axs[1].set_ylim(-5, 350)
# axs[1].set_xlim(-1, 3610)
# axs[0].grid(True, ls="-.", lw=0.5)
# axs[1].grid(True, ls="-.", lw=0.5)
# axs[0].set_ylabel("Total Infectados")
# axs[1].set_ylabel("Atual Infectados")
# axs[1].set_xlabel("Timestep")

# for k in np.arange(10, 180, 10):
#     arq_tempo[k] = {}
#     arq_tempo[k]["arquivos"] = []
#     for cont in range(10,20,1):
#         arq_tempo[k]["arquivos"].append(f'infectiontime_{k}_{cont}')
#     arq_tempo[k]["dados"] = read_logs(arq_tempo[k]["arquivos"])

#     ys = []
#     errs = []
#     xs = np.arange(total_steps)
#     for d in arq_tempo[k]["dados"]["total_infectados"]:
#         ys.append(d["mean"])
#         errs.append(d["std"])
#     axs[0].errorbar(xs, ys, yerr=errs, errorevery=36, label='Tempo {0}'.format(k))

#     ys = []
#     errs = []
#     xs = np.arange(total_steps)
#     for d in arq_tempo[k]["dados"]["atual_infectados"]:
#         ys.append(d["mean"])
#         errs.append(d["std"])
#     axs[1].errorbar(xs, ys, yerr=errs, errorevery=36, label='Tempo {0}'.format(k))


# axs[0].legend(bbox_to_anchor=(0., 1.1, 1., .102), loc='lower left',
#        ncol=3, mode="expand", borderaxespad=0.,shadow=True, fancybox=True)
# plt.savefig("grid_tempo.pdf", bbox_inches="tight")