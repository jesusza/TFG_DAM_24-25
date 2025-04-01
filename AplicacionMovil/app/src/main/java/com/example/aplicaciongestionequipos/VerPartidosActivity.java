package com.example.aplicaciongestionequipos;

import android.os.Bundle;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.RecyclerView;
import com.google.firebase.firestore.FirebaseFirestore;
import com.google.firebase.firestore.QueryDocumentSnapshot;
import java.util.ArrayList;
import java.util.List;

public class VerPartidosActivity extends AppCompatActivity {

    private RecyclerView recyclerPartidos;
    private PartidoAdapter adapter;
    private final List<Partido> listaPartidos = new ArrayList<>();
    private FirebaseFirestore db;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_ver_partidos);

        recyclerPartidos = findViewById(R.id.recyclerPartidos);
        db = FirebaseFirestore.getInstance();

        adapter = new PartidoAdapter(listaPartidos);
        recyclerPartidos.setAdapter(adapter);

        cargarPartidos();
    }

    private void cargarPartidos() {
        db.collection("Calendario").get()
                .addOnSuccessListener(queryDocumentSnapshots -> {
                    listaPartidos.clear();
                    for (QueryDocumentSnapshot doc : queryDocumentSnapshots) {
                        Partido partido = doc.toObject(Partido.class);
                        listaPartidos.add(partido);
                    }
                    adapter.notifyDataSetChanged();
                });
    }
}
