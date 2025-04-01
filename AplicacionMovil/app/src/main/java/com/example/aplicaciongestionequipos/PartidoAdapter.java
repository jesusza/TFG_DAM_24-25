package com.example.aplicaciongestionequipos;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;
import java.util.List;

public class PartidoAdapter extends RecyclerView.Adapter<PartidoAdapter.PartidoViewHolder> {

    private final List<Partido> listaPartidos;

    public PartidoAdapter(List<Partido> listaPartidos) {
        this.listaPartidos = listaPartidos;
    }

    @NonNull
    @Override
    public PartidoViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View vista = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.item_partido, parent, false);
        return new PartidoViewHolder(vista);
    }

    @Override
    public void onBindViewHolder(@NonNull PartidoViewHolder holder, int position) {
        Partido partido = listaPartidos.get(position);
        holder.textEquipos.setText(partido.equipo_local + " vs " + partido.equipo_visitante);
        holder.textFechaHora.setText(partido.fecha + " - " + partido.hora);
        holder.textEstado.setText("Estado: " + partido.estado);
    }

    @Override
    public int getItemCount() {
        return listaPartidos.size();
    }

    public static class PartidoViewHolder extends RecyclerView.ViewHolder {
        TextView textEquipos, textFechaHora, textEstado;

        public PartidoViewHolder(@NonNull View itemView) {
            super(itemView);
            textEquipos = itemView.findViewById(R.id.textEquipos);
            textFechaHora = itemView.findViewById(R.id.textFechaHora);
            textEstado = itemView.findViewById(R.id.textEstado);
        }
    }
}
