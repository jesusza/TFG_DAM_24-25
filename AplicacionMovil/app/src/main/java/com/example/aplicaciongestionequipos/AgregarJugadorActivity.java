package com.example.aplicaciongestionequipos;

import android.os.Bundle;
import android.view.View;
import androidx.appcompat.app.AppCompatActivity;
import com.google.android.material.button.MaterialButton;
import com.google.android.material.snackbar.Snackbar;
import com.google.android.material.textfield.TextInputEditText;
import com.google.firebase.firestore.CollectionReference;
import com.google.firebase.firestore.DocumentSnapshot;
import com.google.firebase.firestore.FirebaseFirestore;

import java.util.HashMap;
import java.util.Map;

public class AgregarJugadorActivity extends AppCompatActivity {

    private TextInputEditText inputNombre, inputEquipo, inputDorsal, inputPosicion;
    private MaterialButton btnGuardar;
    private View rootView;
    private FirebaseFirestore db;
    private CollectionReference jugadoresRef;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_agregar_jugador);

        rootView = findViewById(android.R.id.content);
        db = FirebaseFirestore.getInstance();
        jugadoresRef = db.collection("Jugadores");

        inputNombre = findViewById(R.id.inputNombreJugador);
        inputEquipo = findViewById(R.id.inputEquipoJugador);
        inputDorsal = findViewById(R.id.inputDorsalJugador);
        inputPosicion = findViewById(R.id.inputPosicionJugador);
        btnGuardar = findViewById(R.id.btnGuardarJugador);

        btnGuardar.setOnClickListener(view -> guardarJugador());
    }

    private void guardarJugador() {
        String nombre = inputNombre.getText().toString().trim();
        String equipo = inputEquipo.getText().toString().trim();
        String dorsal = inputDorsal.getText().toString().trim();
        String posicion = inputPosicion.getText().toString().trim();

        if (nombre.isEmpty() || equipo.isEmpty() || dorsal.isEmpty() || posicion.isEmpty()) {
            Snackbar.make(rootView, "Completa todos los campos", Snackbar.LENGTH_SHORT).show();
            return;
        }

        jugadoresRef.get().addOnSuccessListener(querySnapshot -> {
            int maxId = 0;
            for (DocumentSnapshot doc : querySnapshot) {
                String id = doc.getId();
                if (id.startsWith("J")) {
                    try {
                        int num = Integer.parseInt(id.substring(1));
                        if (num > maxId) maxId = num;
                    } catch (NumberFormatException ignored) {}
                }
            }

            String nuevoId = String.format("J%03d", maxId + 1); // Ej: J004

            Map<String, Object> jugador = new HashMap<>();
            jugador.put("nombre", nombre);
            jugador.put("equipo", equipo);
            jugador.put("dorsal", dorsal);
            jugador.put("posicion", posicion);
            jugador.put("goles", "0");
            jugador.put("asistencias", "0");
            jugador.put("tarjetas_amarillas", "0");
            jugador.put("tarjetas_rojas", "0");

            jugadoresRef.document(nuevoId).set(jugador)
                    .addOnSuccessListener(aVoid ->
                            Snackbar.make(rootView, "Jugador guardado con ID: " + nuevoId, Snackbar.LENGTH_SHORT).show())
                    .addOnFailureListener(e ->
                            Snackbar.make(rootView, "Error al guardar jugador", Snackbar.LENGTH_SHORT).show());

        }).addOnFailureListener(e ->
                Snackbar.make(rootView, "Error al generar ID del jugador", Snackbar.LENGTH_SHORT).show());
    }
}
