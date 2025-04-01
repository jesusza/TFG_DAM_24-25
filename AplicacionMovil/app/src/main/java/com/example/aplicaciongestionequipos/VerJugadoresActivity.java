package com.example.aplicaciongestionequipos;

import android.os.Bundle;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.RecyclerView;
import com.google.firebase.firestore.FirebaseFirestore;
import com.google.firebase.firestore.QueryDocumentSnapshot;
import java.util.ArrayList;
import java.util.List;

public class VerJugadoresActivity extends AppCompatActivity {

    private RecyclerView recyclerJugadores;
    private List<Jugador> listaJugadores;
    private JugadorAdapter adapter;
    private FirebaseFirestore db;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_ver_jugadores);

        recyclerJugadores = findViewById(R.id.recyclerJugadores);
        listaJugadores = new ArrayList<>();
        adapter = new JugadorAdapter(listaJugadores);
        recyclerJugadores.setAdapter(adapter);

        db = FirebaseFirestore.getInstance();
        cargarJugadores();
    }

    private void cargarJugadores() {
        db.collection("Jugadores").get()
                .addOnSuccessListener(query -> {
                    listaJugadores.clear();
                    for (QueryDocumentSnapshot doc : query) {
                        Jugador j = doc.toObject(Jugador.class);
                        listaJugadores.add(j);
                    }
                    adapter.notifyDataSetChanged();
                });
    }
}
